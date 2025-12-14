from extension import ma
from marshmallow import fields, validate
from schema.userKkSchema import HumanCapitalSchema

class AdminUpdateStatusSchema(ma.Schema):
    status = fields.String(required=True, validate=validate.OneOf(["P", "T", "B"]))

class AdminKartuKeluargaSchema(ma.Schema):
    id_kk = fields.Integer()
    no_kk = fields.Integer()
    nama_kepala_keluarga = fields.String()
    alamat = fields.String(allow_none=True)
    foto_kk = fields.String(allow_none=True)
    status = fields.String()
    nik = fields.Integer()

admin_update_status_schema = AdminUpdateStatusSchema()
admin_kk_schema = AdminKartuKeluargaSchema()
admin_hc_schema = HumanCapitalSchema()

# Separate schemas for updating KK.status and HumanCapital.status (same validation)
admin_update_kk_status_schema = AdminUpdateStatusSchema()
admin_update_hc_status_schema = AdminUpdateStatusSchema()
