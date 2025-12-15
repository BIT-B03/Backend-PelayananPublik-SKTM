from extension import ma
from marshmallow import fields, validate


class AdminDetailKendaraanSchema(ma.Schema):
    jenis_kendaraan = fields.String(required=True)
    tipe_kendaraan = fields.String(required=True)
    tahun_pembuatan = fields.Integer(required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")


class AdminDetailUpdateSchema(ma.Schema):
    id_detail_kendaraan = fields.Integer(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["B", "T", "P"]))


class AdminAsetNonFinansialSchema(ma.Schema):
    id_aset_non_financial = fields.Integer(dump_only=True)
    nik = fields.Integer(required=True)
    total_kendaraan = fields.Integer(required=True)
    detail_kendaraan = fields.List(fields.Nested(AdminDetailKendaraanSchema), required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")


class AdminStatusSchema(ma.Schema):
    status = fields.String(required=True, validate=validate.OneOf(["B", "T", "P"]))


class AdminUpdateSchema(ma.Schema):
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]))
    detail_kendaraan = fields.List(fields.Nested(AdminDetailUpdateSchema))
