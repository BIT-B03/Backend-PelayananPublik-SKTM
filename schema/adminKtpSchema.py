from extension import ma
from marshmallow import fields, validate

class AdminUpdateStatusSchema(ma.Schema):
    status = fields.String(required=True, validate=validate.OneOf(["P", "T", "B"]))

class AdminKTPSchema(ma.Schema):
    id_ktp = fields.Integer()
    nik = fields.Integer()
    tempat_lahir = fields.String(allow_none=True)
    tanggal_lahir = fields.Date(allow_none=True)
    alamat = fields.String(allow_none=True)
    foto_ktp = fields.String(allow_none=True)
    foto_surat_pengantar_rt_rw = fields.String(allow_none=True)
    status = fields.String(allow_none=True)

admin_update_status_schema = AdminUpdateStatusSchema()
admin_ktp_schema = AdminKTPSchema()

# Summary schema for list endpoints (exclude photo fields to avoid heavy loads)
class AdminKTPSummarySchema(ma.Schema):
    id_ktp = fields.Integer()
    nik = fields.Integer()
    tempat_lahir = fields.String(allow_none=True)
    tanggal_lahir = fields.Date(allow_none=True)
    alamat = fields.String(allow_none=True)
    status = fields.String(allow_none=True)

admin_ktp_summary_schema = AdminKTPSummarySchema(many=False)