from extension import db
from models.kondisirumahModel import KondisiRumah
from models.kondisiekonomiModel import KondisiEkonomi
from models.masyarakatModel import Masyarakat
from schema.adminKondisiEkonomiSchema import (
    admin_update_schema,
)
from schema.userKondisiEkonomiSchema import rumah_schema, ekonomi_schema
from utils.supabase_client import upload_file_from_storage
from marshmallow import ValidationError
from flask import request, jsonify
import os


def list_kondisi_admin(page: int = 1, per_page: int = 100):
    try:
        pag = KondisiRumah.query.paginate(page=page, per_page=per_page, error_out=False)
    except Exception:
        # fallback: return all
        items = KondisiRumah.query.all()
        pag_items = items
    else:
        pag_items = pag.items

    result_list = []
    for rumah in pag_items:
        ekonomi = KondisiEkonomi.query.filter_by(nik=rumah.nik).first()
        entry = {
            "nik": rumah.nik,
            "kondisi_rumah": rumah_schema.dump(rumah) if rumah else None,
            "kondisi_ekonomi": ekonomi_schema.dump(ekonomi) if ekonomi else None,
        }
        result_list.append(entry)

    return jsonify({"data": result_list}), 200


def get_kondisi_admin(nik: int):
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()
    if not rumah and not ekonomi:
        return jsonify({"message": "Not found"}), 404

    result = {
        "nik": nik,
        "kondisi_rumah": rumah_schema.dump(rumah) if rumah else None,
        "kondisi_ekonomi": ekonomi_schema.dump(ekonomi) if ekonomi else None,
    }
    return jsonify({"data": result}), 200


def update_kondisi_admin(nik: int, payload: dict = None, files: dict = None):
    # payload may be JSON or form; files may be FileStorage mapping
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()

    if not rumah and not ekonomi:
        return jsonify({"message": "Not found"}), 404

    form = payload or request.get_json() or request.form.to_dict()
    file_objs = files or request.files

    # validate incoming update payload (non-strict)
    try:
        _ = admin_update_schema.load(form)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

    # update rumah files if provided
    if file_objs.get("foto_depan_rumah"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_depan_rumah"), "kondisi_rumah", "foto_depan_rumah")
        if rumah:
            rumah.foto_depan_rumah = url
    if file_objs.get("foto_atap"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_atap"), "kondisi_rumah", "foto_atap")
        if rumah:
            rumah.foto_atap = url
    if file_objs.get("foto_lantai"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_lantai"), "kondisi_rumah", "foto_lantai")
        if rumah:
            rumah.foto_lantai = url
    if file_objs.get("foto_kamar_mandi"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_kamar_mandi"), "kondisi_rumah", "foto_kamar_mandi")
        if rumah:
            rumah.foto_kamar_mandi = url

    # update ekonomi numeric fields
    if form.get("nominal_slip_gaji") is not None:
        try:
            val = int(form.get("nominal_slip_gaji"))
        except (TypeError, ValueError):
            return jsonify({"message": "nominal_slip_gaji harus berupa angka"}), 400
        if ekonomi:
            ekonomi.nominal_slip_gaji = val

    if form.get("daya_listrik_va") is not None:
        try:
            val = int(form.get("daya_listrik_va"))
        except (TypeError, ValueError):
            return jsonify({"message": "daya_listrik_va harus berupa angka"}), 400
        if ekonomi:
            ekonomi.daya_listrik_va = val

    # update ekonomi files
    if file_objs.get("foto_slip_gaji"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_slip_gaji"), "kondisi_ekonomi", "foto_slip_gaji")
        if ekonomi:
            ekonomi.foto_slip_gaji = url
    if file_objs.get("foto_token_listrik"):
        url = upload_file_from_storage(bucket, nik, file_objs.get("foto_token_listrik"), "kondisi_ekonomi", "foto_token_listrik")
        if ekonomi:
            ekonomi.foto_token_listrik = url

    db.session.commit()

    updated = {
        "nik": nik,
        "kondisi_rumah": rumah_schema.dump(rumah) if rumah else None,
        "kondisi_ekonomi": ekonomi_schema.dump(ekonomi) if ekonomi else None,
    }
    return jsonify({"message": "Updated", "data": updated}), 200


def delete_kondisi_admin(nik: int):
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()

    if not rumah and not ekonomi:
        return jsonify({"message": "Not found"}), 404

    if rumah:
        db.session.delete(rumah)
    if ekonomi:
        db.session.delete(ekonomi)

    db.session.commit()
    return jsonify({"message": "Deleted"}), 200
