from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from extension import db
from models.asetnonfinansialModel import AsetNonFinancial
from models.detailkendaraanModel import DetailKendaraan
from schema.userasetNonfinansialSchema import (
    UserAsetNonFinansialSchema,
    DetailKendaraanSchema,
)
from marshmallow import ValidationError


user_schema = UserAsetNonFinansialSchema()
detail_schema = DetailKendaraanSchema(many=True)


def create_user_aset():
    if request.method != 'POST':
        return jsonify({"message": "Method Not Allowed"}), 405

    payload = request.get_json() or {}
    # Prefer NIK from JWT identity so frontend doesn't need to provide NIK
    try:
        identity = get_jwt_identity()
        nik = int(identity)
    except Exception:
        try:
            nik = int(payload.get("nik"))
        except Exception:
            return jsonify({"message": "Missing or invalid nik"}), 400

    # check existing
    if AsetNonFinancial.query.filter_by(nik=nik).first():
        return jsonify({"message": "Data for this nik already exists"}), 400

    # ensure payload contains nik for schema validation when identity provided
    try:
        payload["nik"] = nik
        data = user_schema.load(payload)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

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

    return jsonify({"message": "Created", "data": user_schema.dump(aset)}), 201


def get_user_aset(nik: int):
    if request.method != 'GET':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return jsonify({"data": None, "message": "Not found"}), 200

    return jsonify({"data": user_schema.dump(aset)}), 200


def update_user_aset(nik: int):
    if request.method != 'PUT':
        return jsonify({"message": "Method Not Allowed"}), 405

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    payload = request.get_json() or {}

    # If aset not found, treat PUT as upsert: create new resource
    if not aset:
        try:
            data = user_schema.load(payload)
        except ValidationError as ve:
            return jsonify({"message": "Validation error", "errors": ve.messages}), 400
        except Exception as e:
            return jsonify({"message": "Validation error", "errors": str(e)}), 400

        aset = AsetNonFinancial(nik=nik, total_kendaraan=data.get("total_kendaraan"), status=data.get("status", "P"))
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

        return jsonify({"message": "Created", "data": user_schema.dump(aset)}), 201

    # allow partial updates
    try:
        data = user_schema.load(payload, partial=True)
    except ValidationError as ve:
        return jsonify({"message": "Validation error", "errors": ve.messages}), 400
    except Exception as e:
        return jsonify({"message": "Validation error", "errors": str(e)}), 400

    if "total_kendaraan" in data:
        aset.total_kendaraan = data["total_kendaraan"]
    if "status" in data:
        aset.status = data["status"]

    # if detail_kendaraan provided, replace existing list
    if "detail_kendaraan" in data:
        # remove existing
        aset.detail_kendaraan = []
        for item in data.get("detail_kendaraan", []):
            dk = DetailKendaraan(
                jenis_kendaraan=item["jenis_kendaraan"],
                tipe_kendaraan=item["tipe_kendaraan"],
                tahun_pembuatan=item["tahun_pembuatan"],
                status=item.get("status", "P"),
            )
            aset.detail_kendaraan.append(dk)

    db.session.commit()

    return jsonify({"message": "Updated", "data": user_schema.dump(aset)}), 200


def update_user_aset_self_controller():
    # wrapper that uses NIK from JWT identity so frontend doesn't need to provide nik in path
    try:
        identity = get_jwt_identity()
        nik = int(identity)
    except Exception:
        return jsonify({"message": "Missing or invalid identity token"}), 401

    # call existing update handler which reads request context
    return update_user_aset(nik)
