from extension import db
from models.kondisirumahModel import KondisiRumah
from models.kondisiekonomiModel import KondisiEkonomi
from schema.userKondisiEkonomiSchema import (
    UserKondisiEkonomiSchema,
    KondisiRumahSchema,
    KondisiEkonomiSchema,
)
from utils.supabase_client import upload_file
from werkzeug.utils import secure_filename
import os
from marshmallow import ValidationError
from uuid import uuid4

user_schema = UserKondisiEkonomiSchema()
rumah_schema = KondisiRumahSchema()
ekonomi_schema = KondisiEkonomiSchema()


def _upload_and_get_url(nik: int, file_storage, bucket: str, dest_folder: str, field_name: str):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename or field_name)
    base, ext = os.path.splitext(filename)
    unique_name = f"{base}_{uuid4().hex}{ext}"
    path = f"{nik}/{dest_folder}/{unique_name}"
    file_bytes = file_storage.read()
    url = upload_file(bucket, path, file_bytes, content_type=file_storage.mimetype)
    return url


def create_user_kondisi(payload: dict, files: dict):
    # payload: dict from form (nik, nominal_slip_gaji, daya_listrik_va optional)
    # files: dict-like from request.files
    try:
        nik = int(payload.get("nik"))
    except Exception:
        return {"message": "Missing or invalid nik"}, 400

    # check existing
    if KondisiRumah.query.filter_by(nik=nik).first() or KondisiEkonomi.query.filter_by(nik=nik).first():
        return {"message": "Data for this nik already exists"}, 400

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

    # upload expected files and build nested payload
    kondisi_rumah = {}
    kondisi_ekonomi = {}

    # house photos
    kondisi_rumah["foto_depan_rumah"] = _upload_and_get_url(nik, files.get("foto_depan_rumah"), bucket, "kondisi_rumah", "foto_depan_rumah")
    kondisi_rumah["foto_atap"] = _upload_and_get_url(nik, files.get("foto_atap"), bucket, "kondisi_rumah", "foto_atap")
    kondisi_rumah["foto_lantai"] = _upload_and_get_url(nik, files.get("foto_lantai"), bucket, "kondisi_rumah", "foto_lantai")
    kondisi_rumah["foto_kamar_mandi"] = _upload_and_get_url(nik, files.get("foto_kamar_mandi"), bucket, "kondisi_rumah", "foto_kamar_mandi")

    # ekonomi photos and fields
    kondisi_ekonomi["nominal_slip_gaji"] = int(payload.get("nominal_slip_gaji")) if payload.get("nominal_slip_gaji") else None
    kondisi_ekonomi["foto_slip_gaji"] = _upload_and_get_url(nik, files.get("foto_slip_gaji"), bucket, "kondisi_ekonomi", "foto_slip_gaji")
    kondisi_ekonomi["daya_listrik_va"] = int(payload.get("daya_listrik_va")) if payload.get("daya_listrik_va") else None
    kondisi_ekonomi["foto_token_listrik"] = _upload_and_get_url(nik, files.get("foto_token_listrik"), bucket, "kondisi_ekonomi", "foto_token_listrik")

    # build final payload for validation
    final_payload = {
        "nik": nik,
        "kondisi_rumah": kondisi_rumah,
        "kondisi_ekonomi": kondisi_ekonomi,
    }

    # debug info: which files were received and what URLs we generated
    print("[DEBUG] received file keys:", list(files.keys()))
    print("[DEBUG] final_payload for validation:", final_payload)

    # fail-fast: if client sent a file but upload did not produce a URL, return explicit error
    upload_failures = []
    # check rumah fields
    for fld in ("foto_depan_rumah", "foto_atap", "foto_lantai", "foto_kamar_mandi"):
        if files.get(fld) and not kondisi_rumah.get(fld):
            upload_failures.append(fld)
    # check ekonomi fields
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
        # include structured marshmallow messages plus helpful debug context
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


def update_user_kondisi(nik: int, payload: dict, files: dict):
    # allow partial update and file replacement
    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()

    if not rumah and not ekonomi:
        return {"message": "Not found"}, 404

    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "public")

    # update rumah files
    if files.get("foto_depan_rumah"):
        url = _upload_and_get_url(nik, files.get("foto_depan_rumah"), bucket, "kondisi_rumah", "foto_depan_rumah")
        if rumah:
            rumah.foto_depan_rumah = url
    if files.get("foto_atap"):
        url = _upload_and_get_url(nik, files.get("foto_atap"), bucket, "kondisi_rumah", "foto_atap")
        if rumah:
            rumah.foto_atap = url
    if files.get("foto_lantai"):
        url = _upload_and_get_url(nik, files.get("foto_lantai"), bucket, "kondisi_rumah", "foto_lantai")
        if rumah:
            rumah.foto_lantai = url
    if files.get("foto_kamar_mandi"):
        url = _upload_and_get_url(nik, files.get("foto_kamar_mandi"), bucket, "kondisi_rumah", "foto_kamar_mandi")
        if rumah:
            rumah.foto_kamar_mandi = url

    # update ekonomi fields and files
    if payload.get("nominal_slip_gaji"):
        if ekonomi:
            ekonomi.nominal_slip_gaji = int(payload.get("nominal_slip_gaji"))
    if files.get("foto_slip_gaji"):
        url = _upload_and_get_url(nik, files.get("foto_slip_gaji"), bucket, "kondisi_ekonomi", "foto_slip_gaji")
        if ekonomi:
            ekonomi.foto_slip_gaji = url
    if payload.get("daya_listrik_va"):
        if ekonomi:
            ekonomi.daya_listrik_va = int(payload.get("daya_listrik_va"))
    if files.get("foto_token_listrik"):
        url = _upload_and_get_url(nik, files.get("foto_token_listrik"), bucket, "kondisi_ekonomi", "foto_token_listrik")
        if ekonomi:
            ekonomi.foto_token_listrik = url

    db.session.commit()

    updated = get_user_kondisi(nik)
    return {"message": "Updated", "data": updated}, 200
