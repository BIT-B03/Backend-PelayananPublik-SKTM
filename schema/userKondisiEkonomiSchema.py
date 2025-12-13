from extension import ma
from marshmallow import fields, validate


class KondisiRumahSchema(ma.Schema):
    foto_depan_rumah = fields.String(required=True)
    foto_atap = fields.String(required=True)
    foto_lantai = fields.String(required=True)
    foto_kamar_mandi = fields.String(required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")


class KondisiEkonomiSchema(ma.Schema):
    nominal_slip_gaji = fields.Integer(required=True)
    foto_slip_gaji = fields.String(required=True)
    daya_listrik_va = fields.Integer(required=False, allow_none=True)
    foto_token_listrik = fields.String(required=True)
    status = fields.String(validate=validate.OneOf(["B", "T", "P"]), missing="P")


class UserKondisiEkonomiSchema(ma.Schema):
    nik = fields.Integer(required=True)
    kondisi_rumah = fields.Nested(KondisiRumahSchema, required=True)
    kondisi_ekonomi = fields.Nested(KondisiEkonomiSchema, required=True)
