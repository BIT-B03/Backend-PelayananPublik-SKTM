from flask import jsonify, request
from extension import db
from models.asetnonfinansialModel import AsetNonFinancial
from models.detailkendaraanModel import DetailKendaraan
from schema.adminAsetNonfinansialSchema import (
    AdminAsetNonFinansialSchema,
    AdminStatusSchema,
    AdminUpdateSchema,
)
from marshmallow import ValidationError


admin_schema = AdminAsetNonFinansialSchema()
admin_status_schema = AdminStatusSchema()


def list_asets(page: int = 1, per_page: int = 100):
    if request.method != 'GET':
        return jsonify({"message": "Method Not Allowed"}), 405

    q = AsetNonFinancial.query
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    items = [admin_schema.dump(aset) for aset in pagination.items]

    return jsonify({"total": pagination.total, "page": pagination.page, "per_page": pagination.per_page, "items": items}), 200


def get_aset_by_id(id_aset: int):
    if request.method != 'GET':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(id_aset_non_financial=id_aset).first()
    if not aset:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"data": admin_schema.dump(aset)}), 200


def get_aset_by_nik(nik: int):
    if request.method != 'GET':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"data": admin_schema.dump(aset)}), 200


def create_aset_admin():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed"}), 405

    payload = request.get_json() or {}
    try:
        data = admin_schema.load(payload)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

    nik = data["nik"]
    if AsetNonFinancial.query.filter_by(nik=nik).first():
        return jsonify({"message": "Data for this nik already exists"}), 400

    aset = AsetNonFinancial(nik=nik, total_kendaraan=data["total_kendaraan"], status=data.get("status", "P"))
    for item in data.get("detail_kendaraan", []):
        dk = DetailKendaraan(
            jenis_kendaraan=item["jenis_kendaraan"],
            tipe_kendaraan=item["tipe_kendaraan"],
            tahun_pembuatan=item["tahun_pembuatan"],
            status=item.get("status", "P"),
        )
        aset.detail_kendaraan.append(dk)

    db.session.add(aset)
    db.session.commit()

    return jsonify({"message": "Created", "id_aset_non_financial": aset.id_aset_non_financial}), 201


def update_aset_admin(nik: int):
    if request.method != 'PUT':
        return jsonify({"message": "Method Not Allowed"}), 405

    payload = request.get_json() or {}

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return jsonify({"message": "Not found"}), 404

    try:
        update_schema = AdminUpdateSchema()
        data = update_schema.load(payload)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

    changed = False
    if "status" in data and data["status"] is not None:
        aset.status = data["status"]
        changed = True

    if data.get("detail_kendaraan"):
        for dk_item in data["detail_kendaraan"]:
            dk = DetailKendaraan.query.filter_by(id_detail_kendaraan=dk_item["id_detail_kendaraan"]).first()
            if not dk:
                continue
            if dk.id_aset_non_financial != aset.id_aset_non_financial:
                continue
            dk.status = dk_item["status"]
            changed = True

    if changed:
        db.session.commit()

    return jsonify({"message": "Status updated", "nik": nik, "id_aset_non_financial": aset.id_aset_non_financial, "status": aset.status}), 200


def delete_aset_admin(nik: int):
    if request.method != 'DELETE':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return jsonify({"message": "Not found"}), 404
    db.session.delete(aset)
    db.session.commit()
    return jsonify({"message": "Deleted", "nik": nik}), 200


def delete_aset_by_nik(nik: int):
    if request.method != 'DELETE':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return jsonify({"message": "Not found"}), 404
    db.session.delete(aset)
    db.session.commit()
    return jsonify({"message": "Deleted", "nik": nik}), 200
