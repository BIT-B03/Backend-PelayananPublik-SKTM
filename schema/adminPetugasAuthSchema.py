from extension import ma
from marshmallow import fields, validate


class PetugasLoginSchema(ma.Schema):
    nip = fields.Integer(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


petugas_login_schema = PetugasLoginSchema()
