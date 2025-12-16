from flask import jsonify, request
from utils.supabase_client import resolve_image_url as _resolve_image_url
from sqlalchemy.exc import IntegrityError
from extension import db
from models.kartukeluargaModel import KartuKeluarga
from models.humancapitalModel import HumanCapital
from schema.adminKkSchema import (
    admin_kk_schema,
    admin_hc_schema,
    admin_update_kk_status_schema,
    admin_update_hc_status_schema,
)
from marshmallow import ValidationError

def update_kartu_keluarga_status_controller(nik: int):
    try:
        if request.method != 'PUT':
            return jsonify({"message": "Method Not Allowed"}), 405

        data = request.get_json() or {}
        try:
            validated = admin_update_kk_status_schema.load(data)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400
        new_status = validated.get('status')

        kk = KartuKeluarga.query.filter_by(nik=nik).first()
        if not kk:
            return jsonify({"message": f"Kartu Keluarga untuk nik {nik} tidak ditemukan"}), 404

        kk.status = new_status
        db.session.commit()

        response = admin_kk_schema.dump(kk)
        # include human capital info if present
        hc = HumanCapital.query.filter_by(nik=kk.nik).first()
        response['human_capital'] = admin_hc_schema.dump(hc) if hc else None

        return jsonify({"message": "Status Kartu Keluarga berhasil diperbarui", "data": response}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def get_all_kartu_keluarga_admin_controller():
    try:
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        kks = KartuKeluarga.query.order_by(KartuKeluarga.id_kk.desc()).all()
        if not kks:
            return jsonify({"message": "Tidak ada data Kartu Keluarga yang ditemukan"}), 404

        data = []
        for kk in kks:
            item = admin_kk_schema.dump(kk)
            hc = HumanCapital.query.filter_by(nik=item.get('nik')).first()
            item['human_capital'] = admin_hc_schema.dump(hc) if hc else None
            # resolve foto_kk if present
            if isinstance(item, dict) and item.get('foto_kk'):
                item['foto_kk'] = _resolve_image_url(item.get('foto_kk'))
            data.append(item)

        return jsonify({"message": "Data Kartu Keluarga berhasil diambil", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def get_kartu_keluarga_detail_admin_controller(nik: int):
    try:
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        kk = KartuKeluarga.query.filter_by(nik=nik).first()
        if not kk:
            return jsonify({"message": f"Kartu Keluarga untuk nik {nik} tidak ditemukan"}), 404

        response_data = admin_kk_schema.dump(kk)
        hc = HumanCapital.query.filter_by(nik=nik).first()
        response_data['human_capital'] = admin_hc_schema.dump(hc) if hc else None

        # resolve foto_kk
        if isinstance(response_data, dict) and response_data.get('foto_kk'):
            response_data['foto_kk'] = _resolve_image_url(response_data.get('foto_kk'))

        return jsonify({"message": "Data Kartu Keluarga berhasil diambil", "data": response_data}), 200

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def update_human_capital_status_controller(nik: int):
    try:
        if request.method != 'PUT':
            return jsonify({"message": "Method Not Allowed"}), 405

        data = request.get_json() or {}
        try:
            validated = admin_update_hc_status_schema.load(data)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400
        new_status = validated.get('status')

        kk = KartuKeluarga.query.filter_by(nik=nik).first()
        if not kk:
            return jsonify({"message": f"Kartu Keluarga untuk nik {nik} tidak ditemukan"}), 404

        hc = HumanCapital.query.filter_by(nik=nik).first()
        if not hc:
            return jsonify({"message": f"HumanCapital untuk nik {nik} tidak ditemukan"}), 404

        hc.status = new_status
        db.session.commit()

        response = admin_hc_schema.dump(hc)
        return jsonify({"message": "Status HumanCapital berhasil diperbarui", "data": response}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def delete_kartu_keluarga_controller(nik: int):
    try:
        if request.method != 'DELETE':
            return jsonify({"message": "Method Not Allowed"}), 405

        kk = KartuKeluarga.query.filter_by(nik=nik).first()
        if not kk:
            return jsonify({"message": f"Kartu Keluarga untuk nik {nik} tidak ditemukan"}), 404

        kk_nik = kk.nik
        hc = HumanCapital.query.filter_by(nik=kk_nik).first()

        db.session.delete(kk)
        db.session.commit()

        if hc:
            return jsonify({"message": "Kartu Keluarga berhasil dihapus. HumanCapital terkait tetap dipertahankan.", "nik": kk_nik}), 200
        else:
            return jsonify({"message": "Kartu Keluarga berhasil dihapus"}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500