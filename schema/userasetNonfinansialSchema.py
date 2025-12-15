from extension import ma
from marshmallow import fields, validate
# Schemas for User Aset Non-Finansial

class DetailKendaraanSchema(ma.Schema):
    id_detail_kendaraan = fields.Integer(dump_only=True)
    jenis_kendaraan = fields.String(required=True)
    tipe_kendaraan = fields.String(required=True)
    tahun_pembuatan = fields.Integer(required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")


class UserAsetNonFinansialSchema(ma.Schema):
    nik = fields.Integer(required=True)
    total_kendaraan = fields.Integer(required=True)
    detail_kendaraan = fields.List(fields.Nested(DetailKendaraanSchema), required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")
