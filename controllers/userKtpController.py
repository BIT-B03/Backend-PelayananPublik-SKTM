from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from extension import db
from models.ktpModel import KTP
from schema.userKtpSchema import ktp_schema, ktp_create_schema
from marshmallow import ValidationError
from utils.supabase_client import upload_file_from_storage
import os

# [CREATE] POST KTP
def create_ktp_controller():
	try:
		if request.method != 'POST':
			return jsonify({"message": "Method Not Allowed"}), 405

		identity = get_jwt_identity()
		try:
			nik_from_token = int(identity)
		except Exception:
			return jsonify({"message": "Invalid identity in token"}), 500

		data = request.form.to_dict() or request.get_json(silent=True) or {}

		bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")
		
		files = request.files or {}
		if files.get('foto_ktp'):
			data['foto_ktp'] = upload_file_from_storage(bucket, nik_from_token, files.get('foto_ktp'), 'ktp', 'foto_ktp')
		if files.get('foto_surat_pengantar_rt_rw'):
			data['foto_surat_pengantar_rt_rw'] = upload_file_from_storage(bucket, nik_from_token, files.get('foto_surat_pengantar_rt_rw'), 'ktp', 'foto_surat_pengantar_rt_rw')

		try:
			ktp = ktp_create_schema.load(data)
			ktp.nik = nik_from_token
		except ValidationError as ve:
			return jsonify({"message": "Validation error", "errors": ve.messages}), 400

		db.session.add(ktp)
		db.session.commit()

		return jsonify({
			"message": "KTP berhasil dibuat",
			"data": ktp_schema.dump(ktp)
		}), 200

	except IntegrityError as ie:
			db.session.rollback()
			return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
	except Exception as e:
		db.session.rollback()
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

# [READ] KTP by ID
def get_ktp_detail_controller(nik: int):
	try:
		if request.method != 'GET':
			return jsonify({"message": "Method Not Allowed"}), 405

		ktp = KTP.query.filter_by(nik=nik).first()
		if not ktp:
			return jsonify({"message": f"KTP untuk nik {nik} tidak ditemukan"}), 404

		return jsonify({
			"message": "Data KTP berhasil diambil",
			"data": ktp_schema.dump(ktp)
		}), 200

	except Exception as e:
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

# [UPDATE] KTP by ID
def update_ktp_controller(nik: int):
	try:
		if request.method != 'PUT':
			return jsonify({"message": "Method Not Allowed"}), 405

		identity = get_jwt_identity()
		try:
			nik_from_token = int(identity)
		except Exception:
			return jsonify({"message": "Invalid identity in token"}), 500

		ktp = KTP.query.filter_by(nik=nik).first()
		if not ktp:
			return jsonify({"message": "KTP tidak ditemukan"}), 404
		if ktp.nik != nik_from_token:
			return jsonify({"message": "KTP tidak ditemukan"}), 404

		data = request.form.to_dict() or request.get_json(silent=True) or {}
		files = request.files or {}
		bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

		for field in ["tempat_lahir", "tanggal_lahir", "alamat"]:
			if field in data:
				setattr(ktp, field, data[field])

		if files.get('foto_ktp'):
			url = upload_file_from_storage(bucket, nik_from_token, files.get('foto_ktp'), 'ktp', 'foto_ktp')
			if url:
				ktp.foto_ktp = url
		if files.get('foto_surat_pengantar_rt_rw'):
			url = upload_file_from_storage(bucket, nik_from_token, files.get('foto_surat_pengantar_rt_rw'), 'ktp', 'foto_surat_pengantar_rt_rw')
			if url:
				ktp.foto_surat_pengantar_rt_rw = url

		db.session.commit()
		return jsonify({"message": "KTP berhasil diperbarui", "data": ktp_schema.dump(ktp)}), 200

	except IntegrityError as ie:
		db.session.rollback()
		return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 400
	except Exception as e:
		db.session.rollback()
		return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500