from extension import ma
from marshmallow import fields, post_load


class ProfilSchema(ma.Schema):
    nik = fields.Integer()
    nama = fields.String(allow_none=True)
    alamat = fields.String(allow_none=True)
    no_kk = fields.Integer(allow_none=True)
    tempat_lahir = fields.String(allow_none=True)
    tanggal_lahir = fields.Date(allow_none=True)
    nomor_hp = fields.String(allow_none=True)
    email = fields.Email(allow_none=True)


class ProfilUpdateSchema(ma.Schema):
    nama = fields.String(required=False, allow_none=True)
    alamat = fields.String(required=False, allow_none=True)
    no_kk = fields.Integer(required=False, allow_none=True)
    tempat_lahir = fields.String(required=False, allow_none=True)
    tanggal_lahir = fields.Date(required=False, allow_none=True)
    nomor_hp = fields.String(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)


profil_schema = ProfilSchema()
profil_update_schema = ProfilUpdateSchema()
