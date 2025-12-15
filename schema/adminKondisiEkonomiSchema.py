from marshmallow import Schema, fields


class AdminKondisiRumahSchema(Schema):
    foto_depan_rumah = fields.String(allow_none=True)
    foto_atap = fields.String(allow_none=True)
    foto_lantai = fields.String(allow_none=True)
    foto_kamar_mandi = fields.String(allow_none=True)


class AdminKondisiEkonomiSchema(Schema):
    nominal_slip_gaji = fields.Integer(allow_none=True)
    foto_slip_gaji = fields.String(allow_none=True)
    daya_listrik_va = fields.Integer(allow_none=True)
    foto_token_listrik = fields.String(allow_none=True)


class AdminKondisiUpdateSchema(Schema):
    kondisi_rumah = fields.Nested(AdminKondisiRumahSchema, allow_none=True)
    kondisi_ekonomi = fields.Nested(AdminKondisiEkonomiSchema, allow_none=True)


admin_rumah_schema = AdminKondisiRumahSchema()
admin_ekonomi_schema = AdminKondisiEkonomiSchema()
admin_update_schema = AdminKondisiUpdateSchema()
