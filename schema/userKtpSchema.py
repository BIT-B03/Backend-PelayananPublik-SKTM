from extension import ma
from marshmallow import fields
from marshmallow import post_load

class KTPCreateSchema(ma.Schema):
    tempat_lahir = fields.String(allow_none=True)
    tanggal_lahir = fields.Date(allow_none=True)
    alamat = fields.String(allow_none=True)
    foto_ktp = fields.String(allow_none=True)
    foto_surat_pengantar_rt_rw = fields.String(allow_none=True)
    status = fields.String(allow_none=True)

    @post_load
    def make_ktp(self, data, **kwargs):
        from models.ktpModel import KTP
        if 'status' in data and data.get('status') is not None:
            return KTP(**data)
        return KTP(**data, status='P')

class KTPSchema(ma.Schema):
    id_ktp = fields.Integer()
    nik = fields.Integer(required=True)
    tempat_lahir = fields.String(allow_none=True)
    tanggal_lahir = fields.Date(allow_none=True)
    alamat = fields.String(allow_none=True)
    foto_ktp = fields.String(allow_none=True)
    foto_surat_pengantar_rt_rw = fields.String(allow_none=True)
    status = fields.String(allow_none=True)

ktp_schema = KTPSchema()
ktps_schema = KTPSchema(many=True)
ktp_create_schema = KTPCreateSchema()