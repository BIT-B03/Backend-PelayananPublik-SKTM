from extension import db
from utils.supabase_client import resolve_image_url as _resolve_image_url
from models.kondisirumahModel import KondisiRumah
from models.kondisiekonomiModel import KondisiEkonomi
from models.masyarakatModel import Masyarakat
from schema.adminKondisiEkonomiSchema import admin_status_update_schema
from schema.userKondisiEkonomiSchema import rumah_schema, ekonomi_schema, rumah_summary_schema, ekonomi_summary_schema
from marshmallow import ValidationError
from flask import request, jsonify


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
        # use summary schemas to avoid including photo fields in listing
        entry = {
            "nik": rumah.nik,
            "kondisi_rumah": rumah_summary_schema.dump(rumah) if rumah else None,
            "kondisi_ekonomi": ekonomi_summary_schema.dump(ekonomi) if ekonomi else None,
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
    # Resolve foto_* fields
    kr = result.get("kondisi_rumah")
    if isinstance(kr, dict):
        for k, v in list(kr.items()):
            if k.startswith("foto_"):
                kr[k] = _resolve_image_url(v)

    ke = result.get("kondisi_ekonomi")
    if isinstance(ke, dict):
        for k, v in list(ke.items()):
            if k.startswith("foto_"):
                ke[k] = _resolve_image_url(v)

    return jsonify({"data": result}), 200


def update_kondisi_admin(nik: int):
    """Admin endpoint: only allow updating status for rumah and ekonomi via schema validation."""
    if request.method != 'PUT':
        return jsonify({"message": "Method Not Allowed"}), 405

    rumah = KondisiRumah.query.filter_by(nik=nik).first()
    ekonomi = KondisiEkonomi.query.filter_by(nik=nik).first()

    if not rumah and not ekonomi:
        return jsonify({"message": "Not found"}), 404

    payload = request.get_json() or {}
    try:
        data = admin_status_update_schema.load(payload)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

    changed = False
    if data.get("kondisi_rumah_status") is not None and rumah:
        rumah.status = data.get("kondisi_rumah_status")
        changed = True
    if data.get("kondisi_ekonomi_status") is not None and ekonomi:
        ekonomi.status = data.get("kondisi_ekonomi_status")
        changed = True

    if changed:
        db.session.commit()

    updated = {
        "nik": nik,
        "kondisi_rumah": rumah_schema.dump(rumah) if rumah else None,
        "kondisi_ekonomi": ekonomi_schema.dump(ekonomi) if ekonomi else None,
    }
    return jsonify({"message": "Status updated", "data": updated}), 200


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
