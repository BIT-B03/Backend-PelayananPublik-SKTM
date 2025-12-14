from extension import db
from models.kondisirumahModel import KondisiRumah
from models.kondisiekonomiModel import KondisiEkonomi
from models.masyarakatModel import Masyarakat
from schema.userKondisiEkonomiSchema import user_schema, rumah_schema, ekonomi_schema
from utils.supabase_client import upload_file_from_storage
import os
from marshmallow import ValidationError
from flask import request, jsonify

def create_user_kondisi(payload: dict, files: dict):
    try:
        nik = int(payload.get("nik"))
    except Exception:
        return {"message": "Missing or invalid nik"}, 400

    # ensure the masyarakat (person) exists before inserting kondisi records
    if not Masyarakat.query.filter_by(nik=nik).first():
        return {"message": "Masyarakat dengan nik tidak ditemukan. Silakan buat data masyarakat terlebih dahulu."}, 404

    if KondisiRumah.query.filter_by(nik=nik).first() or KondisiEkonomi.query.filter_by(nik=nik).first():
        return {"message": "Data for this nik already exists"}, 400

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

    kondisi_rumah = {}
    kondisi_ekonomi = {}

    # house photos
    kondisi_rumah["foto_depan_rumah"] = upload_file_from_storage(bucket, nik, files.get("foto_depan_rumah"), "kondisi_rumah", "foto_depan_rumah")
    kondisi_rumah["foto_atap"] = upload_file_from_storage(bucket, nik, files.get("foto_atap"), "kondisi_rumah", "foto_atap")
    kondisi_rumah["foto_lantai"] = upload_file_from_storage(bucket, nik, files.get("foto_lantai"), "kondisi_rumah", "foto_lantai")
    kondisi_rumah["foto_kamar_mandi"] = upload_file_from_storage(bucket, nik, files.get("foto_kamar_mandi"), "kondisi_rumah", "foto_kamar_mandi")

    # ekonomi photos and fields
    # validate numeric inputs and return 400 on invalid types (avoid 500 internal error)
    nominal_raw = payload.get("nominal_slip_gaji")
    if nominal_raw:
        try:
            nominal_val = int(nominal_raw)
        except (TypeError, ValueError):
            return {"message": "nominal_slip_gaji harus berupa angka (integer)"}, 400
    else:
        nominal_val = None
    kondisi_ekonomi["nominal_slip_gaji"] = nominal_val
    kondisi_ekonomi["foto_slip_gaji"] = upload_file_from_storage(bucket, nik, files.get("foto_slip_gaji"), "kondisi_ekonomi", "foto_slip_gaji")
    daya_raw = payload.get("daya_listrik_va")
    if daya_raw:
        try:
            daya_val = int(daya_raw)
        except (TypeError, ValueError):
            return {"message": "daya_listrik_va harus berupa angka (integer)"}, 400
    else:
        daya_val = None
    kondisi_ekonomi["daya_listrik_va"] = daya_val
    kondisi_ekonomi["foto_token_listrik"] = upload_file_from_storage(bucket, nik, files.get("foto_token_listrik"), "kondisi_ekonomi", "foto_token_listrik")

    # build final payload for validation
    final_payload = {
        "nik": nik,
        "kondisi_rumah": kondisi_rumah,
        "kondisi_ekonomi": kondisi_ekonomi,
    }

    # debug info: which files were received and what URLs we generated
    print("[DEBUG] received file keys:", list(files.keys()))
    print("[DEBUG] final_payload for validation:", final_payload)

    upload_failures = []
    for fld in ("foto_depan_rumah", "foto_atap", "foto_lantai", "foto_kamar_mandi"):
        if files.get(fld) and not kondisi_rumah.get(fld):
            upload_failures.append(fld)
    
    for fld in ("foto_slip_gaji", "foto_token_listrik"):
        if files.get(fld) and not kondisi_ekonomi.get(fld):
            upload_failures.append(fld)

    if upload_failures:
        msg = {"message": "Upload failed for files", "failed_fields": upload_failures}
        print("[DEBUG] upload failures:", upload_failures)
        return msg, 502

    # validate
    try:
        data = user_schema.load(final_payload)
    except ValidationError as ve:
        error_payload = {
            "message": "Validation error",
            "errors": ve.messages,
            "debug": {
                "received_file_keys": list(files.keys()),
                "final_payload": final_payload,
            },
        }
        print("[DEBUG] validation failed:", ve.messages)
        return error_payload, 400
    except Exception as e:
        print("[DEBUG] unexpected validation exception:", str(e))
        return {"message": "Validation error", "errors": str(e), "debug": {"final_payload": final_payload}}, 400

    rumah = KondisiRumah(nik=nik, **data["kondisi_rumah"])
    ekonomi = KondisiEkonomi(nik=nik, **data["kondisi_ekonomi"])

    db.session.add(rumah)
    db.session.add(ekonomi)
    db.session.commit()

    result = {
        "nik": nik,
        "kondisi_rumah": rumah_schema.dump(rumah),
        "kondisi_ekonomi": ekonomi_schema.dump(ekonomi),
    }
    return {"message": "Created", "data": result}, 201

def create_user_kondisi_controller():
    form = request.form.to_dict()
    files = request.files
    result, status = create_user_kondisi(form, files)
    return jsonify(result), status

def get_user_kondisi(nik: int):
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()
    if not rumah and not ekonomi:
        return None

    result = {
        "nik": nik,
        "kondisi_rumah": rumah_schema.dump(rumah) if rumah else None,
        "kondisi_ekonomi": ekonomi_schema.dump(ekonomi) if ekonomi else None,
    }
    return result

def get_user_kondisi_controller(nik: int):
    data = get_user_kondisi(nik)
    if not data:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"data": data}), 200

def update_user_kondisi(nik: int, payload: dict, files: dict):
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()

    if not rumah and not ekonomi:
        return {"message": "Not found"}, 404

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

    # update rumah files
    if files.get("foto_depan_rumah"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_depan_rumah"), "kondisi_rumah", "foto_depan_rumah")
        if rumah:
            rumah.foto_depan_rumah = url
    if files.get("foto_atap"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_atap"), "kondisi_rumah", "foto_atap")
        if rumah:
            rumah.foto_atap = url
    if files.get("foto_lantai"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_lantai"), "kondisi_rumah", "foto_lantai")
        if rumah:
            rumah.foto_lantai = url
    if files.get("foto_kamar_mandi"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_kamar_mandi"), "kondisi_rumah", "foto_kamar_mandi")
        if rumah:
            rumah.foto_kamar_mandi = url

    # update ekonomi fields and files
    if payload.get("nominal_slip_gaji"):
        if ekonomi:
            ekonomi.nominal_slip_gaji = int(payload.get("nominal_slip_gaji"))
    if files.get("foto_slip_gaji"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_slip_gaji"), "kondisi_ekonomi", "foto_slip_gaji")
        if ekonomi:
            ekonomi.foto_slip_gaji = url
    if payload.get("daya_listrik_va"):
        if ekonomi:
            ekonomi.daya_listrik_va = int(payload.get("daya_listrik_va"))
    if files.get("foto_token_listrik"):
        url = upload_file_from_storage(bucket, nik, files.get("foto_token_listrik"), "kondisi_ekonomi", "foto_token_listrik")
        if ekonomi:
            ekonomi.foto_token_listrik = url

    db.session.commit()

    updated = get_user_kondisi(nik)
    return {"message": "Updated", "data": updated}, 200

def update_user_kondisi_controller(nik: int):
    form = request.form.to_dict()
    files = request.files
    result, status = update_user_kondisi(nik, form, files)
    return jsonify(result), status