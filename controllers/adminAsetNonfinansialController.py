from extension import db
from models.asetnonfinansialModel import AsetNonFinancial
from models.detailkendaraanModel import DetailKendaraan
from schema.adminAsetNonfinansialSchema import AdminAsetNonFinansialSchema, AdminStatusSchema
from marshmallow import ValidationError


admin_schema = AdminAsetNonFinansialSchema()
admin_status_schema = AdminStatusSchema()


def list_asets(page: int = 1, per_page: int = 100):
    q = AsetNonFinancial.query
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for aset in pagination.items:
        items.append({
            "id_aset_non_financial": aset.id_aset_non_financial,
            "nik": aset.nik,
            "total_kendaraan": aset.total_kendaraan,
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
            "status": aset.status,
        })

    return {"total": pagination.total, "page": pagination.page, "per_page": pagination.per_page, "items": items}, 200
    


def get_aset_by_id(id_aset: int):
    aset = AsetNonFinancial.query.filter_by(id_aset_non_financial=id_aset).first()
    if not aset:
        return {"message": "Not found"}, 404
    return {
        "id_aset_non_financial": aset.id_aset_non_financial,
        "nik": aset.nik,
        "total_kendaraan": aset.total_kendaraan,
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
        "status": aset.status,
    }, 200


def get_aset_by_nik(nik: str):
    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404
    return {
        "id_aset_non_financial": aset.id_aset_non_financial,
        "nik": aset.nik,
        "total_kendaraan": aset.total_kendaraan,
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
        "status": aset.status,
    }, 200


def create_aset_admin(payload: dict):
    try:
        data = admin_schema.load(payload)
    except ValidationError as ve:
        return {"message": "Validation error", "errors": ve.messages}, 400
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 400

    nik = data["nik"]
    if AsetNonFinancial.query.filter_by(nik=nik).first():
        return {"message": "Data for this nik already exists"}, 400

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

    return {"message": "Created", "id_aset_non_financial": aset.id_aset_non_financial}, 201


def update_aset_admin(nik: int, payload: dict):
    """Admin may change `status` of an aset and statuses of its detail_kendaraan by `id_detail_kendaraan`."""
    from schema.adminAsetNonfinansialSchema import AdminUpdateSchema

    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404

    try:
        update_schema = AdminUpdateSchema()
        data = update_schema.load(payload)
    except ValidationError as ve:
        return {"message": "Validation error", "errors": ve.messages}, 400
    except Exception as e:
        return {"message": "Validation error", "errors": str(e)}, 400

    changed = False
    if "status" in data and data["status"] is not None:
        aset.status = data["status"]
        changed = True

    if data.get("detail_kendaraan"):
        for dk_item in data["detail_kendaraan"]:
            dk = DetailKendaraan.query.filter_by(id_detail_kendaraan=dk_item["id_detail_kendaraan"]).first()
            if not dk:
                continue
            # ensure the detail belongs to this aset
            if dk.id_aset_non_financial != aset.id_aset_non_financial:
                continue
            dk.status = dk_item["status"]
            changed = True

    if changed:
        db.session.commit()

    return {"message": "Status updated", "nik": nik, "id_aset_non_financial": aset.id_aset_non_financial, "status": aset.status}, 200


def delete_aset_admin(nik: int):
    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404
    db.session.delete(aset)
    db.session.commit()
    return {"message": "Deleted", "nik": nik}, 200


def delete_aset_by_nik(nik: int):
    aset = AsetNonFinancial.query.filter_by(nik=nik).first()
    if not aset:
        return {"message": "Not found"}, 404
    db.session.delete(aset)
    db.session.commit()
    return {"message": "Deleted", "nik": nik}, 200
