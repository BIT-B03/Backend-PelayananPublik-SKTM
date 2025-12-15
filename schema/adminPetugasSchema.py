from extension import ma
from marshmallow import fields, validate
# Schemas for Admin Petugas

class CreatePetugasSchema(ma.Schema):
    nik = fields.Integer(required=True)
    password = fields.String(required=False, validate=validate.Length(min=6, max=255))
    role = fields.String(required=False, validate=validate.OneOf(["petugas", "admin"]))


class PetugasSchema(ma.Schema):
    nip = fields.Integer()
    nik = fields.Integer()
    role = fields.String()


create_petugas_schema = CreatePetugasSchema()
petugas_schema = PetugasSchema()
