from extension import ma
from marshmallow import fields, validate


class RegisterSchema(ma.Schema):
    nik = fields.Integer(required=True)
    nama = fields.String(required=True, validate=validate.Length(min=1, max=255))
    jenis_kelamin = fields.String(required=True, validate=validate.OneOf(["L", "P"]))
    email = fields.Email(required=True)
    nomor_hp = fields.String(required=True, validate=validate.Length(min=6, max=50))
    password = fields.String(required=True, validate=validate.Length(min=6, max=255))


class LoginSchema(ma.Schema):
    nik = fields.Integer(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=255))
