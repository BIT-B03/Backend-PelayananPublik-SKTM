from flask import jsonify, request
import os
from utils.supabase_client import make_absolute_signed_url as _make_absolute_signed_url, resolve_image_url as _resolve_image_url
from sqlalchemy.exc import IntegrityError
from extension import db
from models.ktpModel import KTP
from schema.adminKtpSchema import admin_ktp_schema, admin_update_status_schema
from marshmallow import ValidationError
from dotenv import load_dotenv

load_dotenv()

def get_all_ktp_admin_controller():
    try:
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        ktps = KTP.query.order_by(KTP.id_ktp.desc()).all()
        if not ktps:
            return jsonify({"message": "Tidak ada data KTP yang ditemukan"}), 404

        data = [admin_ktp_schema.dump(k) for k in ktps]
        # Convert any relative signed paths to absolute signed URLs (refresh token if needed)
        for item in data:
            item["foto_ktp"] = _resolve_image_url(item.get("foto_ktp"))
            item["foto_surat_pengantar_rt_rw"] = _resolve_image_url(item.get("foto_surat_pengantar_rt_rw"))
        return jsonify({"message": "Data KTP berhasil diambil", "count": len(data), "data": data}), 200

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def get_ktp_detail_admin_controller(nik: int):
    try:
        if request.method != 'GET':
            return jsonify({"message": "Method Not Allowed"}), 405

        ktp = KTP.query.filter_by(nik=nik).first()
        if not ktp:
            return jsonify({"message": f"KTP untuk nik {nik} tidak ditemukan"}), 404

        result = admin_ktp_schema.dump(ktp)
        # Convert any relative signed paths to absolute signed URLs (refresh token if needed)
        result["foto_ktp"] = _resolve_image_url(result.get("foto_ktp"))
        result["foto_surat_pengantar_rt_rw"] = _resolve_image_url(result.get("foto_surat_pengantar_rt_rw"))
        return jsonify({"message": "Data KTP berhasil diambil", "data": result}), 200

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def update_ktp_status_controller(nik: int):
    try:
        if request.method != 'PUT':
            return jsonify({"message": "Method Not Allowed"}), 405

        data = request.get_json() or {}
        try:
            validated = admin_update_status_schema.load(data)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 500
        new_status = validated.get('status')

        ktp = KTP.query.filter_by(nik=nik).first()
        if not ktp:
            return jsonify({"message": f"KTP untuk nik {nik} tidak ditemukan"}), 404

        ktp.status = new_status
        db.session.commit()

        return jsonify({"message": "Status KTP berhasil diperbarui", "data": admin_ktp_schema.dump(ktp)}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500

def delete_ktp_controller(nik: int):
    try:
        if request.method != 'DELETE':
            return jsonify({"message": "Method Not Allowed"}), 405
        ktp = KTP.query.filter_by(nik=nik).first()
        if not ktp:
            return jsonify({"message": f"KTP untuk nik {nik} tidak ditemukan"}), 404

        db.session.delete(ktp)
        db.session.commit()

        return jsonify({"message": "KTP berhasil dihapus"}), 200

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": f"Integrity error: {str(ie.orig)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Terjadi kesalahan server: {str(e)}"}), 500