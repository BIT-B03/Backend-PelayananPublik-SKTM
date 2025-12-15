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


def create_user_aset(payload: dict):
    try:
        nik = int(payload.get("nik"))
    except Exception:
        return {"message": "Missing or invalid nik"}, 400

    # check existing
    if AsetNonFinancial.query.filter_by(nik=nik).first():
        return {"message": "Data for this nik already exists"}, 400

    try:
        data = user_schema.load(payload)
    except ValidationError as ve:
        return {"message": "Validation error", "errors": ve.messages}, 400
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 400

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

    result = {
        "nik": nik,
        "total_kendaraan": aset.total_kendaraan,
        "status": aset.status,
        "detail_kendaraan": [
            {
                "id_detail_kendaraan": d.id_detail_kendaraan,
                "jenis_kendaraan": d.jenis_kendaraan,
                "tipe_kendaraan": d.tipe_kendaraan,
                "tahun_pembuatan": int(d.tahun_pembuatan) if d.tahun_pembuatan is not None else None,
                "status": d.status,
            }
            for d in aset.detail_kendaraan
        ],
    }

    return {"message": "Created", "data": result}, 201


def get_user_aset(nik: int):
    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404

    result = {
        "nik": nik,
        "total_kendaraan": aset.total_kendaraan,
        "status": aset.status,
        "detail_kendaraan": [
            {
                "id_detail_kendaraan": d.id_detail_kendaraan,
                "jenis_kendaraan": d.jenis_kendaraan,
                "tipe_kendaraan": d.tipe_kendaraan,
                "tahun_pembuatan": int(d.tahun_pembuatan) if d.tahun_pembuatan is not None else None,
                "status": d.status,
            }
            for d in aset.detail_kendaraan
        ],
    }
    return {"data": result}, 200


def update_user_aset(nik: int, payload: dict):
    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404

    # allow partial updates
    try:
        data = user_schema.load(payload, partial=True)
    except ValidationError as ve:
        return {"message": "Validation error", "errors": ve.messages}, 400
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 400

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

    updated = get_user_aset(nik)
    return {"message": "Updated", "data": updated}, 200
