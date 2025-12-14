from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from extension import db
from models.kartukeluargaModel import KartuKeluarga
from models.humancapitalModel import HumanCapital
from schema.userKkSchema import kk_schema, kk_create_schema, hc_schema
from marshmallow import ValidationError
from utils.supabase_client import upload_file_from_storage
import os

# [CREATE] POST KK
def create_kartu_keluarga_controller():
	try:
		if request.method != 'POST':
			return jsonify({"message": "Method Not Allowed"}), 405

		identity = get_jwt_identity()
		if identity is None:
			return jsonify({"message": "Unauthorized: missing token identity"}), 401
		try:
			nik_from_token = int(identity)
		except (TypeError, ValueError):
			return jsonify({"message": "Unauthorized: invalid token identity format"}), 401

		# Prevent duplicate Kartu Keluarga for the same nik: return 409 Conflict
		existing_kk = KartuKeluarga.query.filter_by(nik=identity if isinstance(identity, int) else nik_from_token).first()
		if existing_kk:
			return jsonify({"message": "Duplikasi input: user ini sudah memiliki Kartu Keluarga"}), 409

		data = request.form.to_dict() or request.get_json(silent=True) or {}

		bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")
		# use shared helper in utils.supabase_client

		files = request.files or {}
		if files.get('foto_kk'):
			data['foto_kk'] = upload_file_from_storage(bucket, nik_from_token, files.get('foto_kk'), 'kk', 'foto_kk')

		try:
			kk = kk_create_schema.load(data)
			# attach nik from token (schema does not declare nik as input field)
			kk.nik = nik_from_token
			# if schema created a related HumanCapital instance, make sure it also has nik set
			if hasattr(kk, '_human_capital') and kk._human_capital is not None:
				kk._human_capital.nik = nik_from_token
		except ValidationError as ve:
			return jsonify({"message": "Validation error", "errors": ve.messages}), 400

		db.session.add(kk)

		hc_obj = HumanCapital.query.filter_by(nik=kk.nik).first()
		if hc_obj:
			if 'tingkat_pendidikan_kepala_keluarga' in data:
				hc_obj.tingkat_pendidikan_kepala_keluarga = data.get('tingkat_pendidikan_kepala_keluarga')
			if 'anak_tidak_sekolah' in data:
				hc_obj.anak_tidak_sekolah = data.get('anak_tidak_sekolah')
			hc_obj.status = 'P'
		else:
			if hasattr(kk, '_human_capital'):
				db.session.add(kk._human_capital)

		db.session.commit()

		hc_response = hc_obj if hc_obj else getattr(kk, '_human_capital', None)
		response_data = kk_schema.dump(kk)
		response_data['human_capital'] = hc_schema.dump(hc_response) if hc_response else None

		return jsonify({"message": "Kartu Keluarga berhasil dibuat", "data": response_data}), 200

	except IntegrityError as ie:
		db.session.rollback()
		return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
	except Exception as e:
		db.session.rollback()
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

# [READ] KK by ID
def get_kartu_keluarga_detail_controller(nik: int):
	try:
		if request.method != 'GET':
			return jsonify({"message": "Method Not Allowed"}), 405

		kk = KartuKeluarga.query.filter_by(nik=nik).first()
		if not kk:
			return jsonify({"message": f"Kartu Keluarga untuk nik {nik} tidak ditemukan"}), 404

		response_data = kk_schema.dump(kk)
		hc = HumanCapital.query.filter_by(nik=kk.nik).first()
		response_data['human_capital'] = hc_schema.dump(hc) if hc else None

		return jsonify({"message": "Data Kartu Keluarga berhasil diambil", "data": response_data}), 200

	except Exception as e:
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

# [UPDATE] KK by ID
def update_kartu_keluarga_controller(nik: int):
	try:
		if request.method != 'PUT':
			return jsonify({"message": "Method Not Allowed"}), 405

		identity = get_jwt_identity()
		if identity is None:
			return jsonify({"message": "Unauthorized: missing token identity"}), 401
		try:
			nik_from_token = int(identity)
		except (TypeError, ValueError):
			return jsonify({"message": "Unauthorized: invalid token identity format"}), 401

		kk = KartuKeluarga.query.filter_by(nik=nik).first()
		if not kk:
			return jsonify({"message": "Kartu Keluarga tidak ditemukan"}), 404

		if kk.nik != nik_from_token:
			return jsonify({"message": "Kartu Keluarga tidak ditemukan"}), 404

		data = request.form.to_dict() or request.get_json(silent=True) or {}

		data['nik'] = nik_from_token
		files = request.files or {}
		bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")
		# use shared helper in utils.supabase_client

		for field in ["no_kk", "nama_kepala_keluarga", "alamat", "foto_kk", "status"]:
			if field in data:
				if field == 'no_kk':
					try:
						setattr(kk, field, int(data[field]))
					except ValueError:
						return jsonify({"message": "no_kk harus berupa 16 digit angka"}), 500
				else:
					setattr(kk, field, data[field])

		if files.get('foto_kk'):
			url = upload_file_from_storage(bucket, nik_from_token, files.get('foto_kk'), 'kk', 'foto_kk')
			if url:
				kk.foto_kk = url

		hc = HumanCapital.query.filter_by(nik=kk.nik).first()
		if hc:
			if 'tingkat_pendidikan_kepala_keluarga' in data:
				hc.tingkat_pendidikan_kepala_keluarga = data.get('tingkat_pendidikan_kepala_keluarga')
			if 'anak_tidak_sekolah' in data:
				hc.anak_tidak_sekolah = data.get('anak_tidak_sekolah')
			if 'status_human' in data:
				hc.status = data.get('status_human')

		db.session.commit()
		response_data = kk_schema.dump(kk)
		response_data['human_capital'] = hc_schema.dump(hc) if hc else None
		return jsonify({"message": "Kartu Keluarga berhasil diperbarui", "data": response_data}), 200

	except IntegrityError as ie:
		db.session.rollback()
		return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
	except Exception as e:
		db.session.rollback()
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500