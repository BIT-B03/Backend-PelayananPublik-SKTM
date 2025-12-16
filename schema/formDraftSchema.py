from marshmallow import Schema, fields, validate


class FormDraftSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    form_type = fields.Str(required=True, validate=validate.Length(max=64))
    data_json = fields.Dict(required=False, allow_none=True)
    fill_progress = fields.Float(required=False, validate=validate.Range(min=0, max=100), missing=0.0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
