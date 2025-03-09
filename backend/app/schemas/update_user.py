from marshmallow import Schema, fields, validate
import re

class UpdateUserSchema(Schema):
    email = fields.Email(required=False)
    first_name = fields.Str(required=False, validate=[
        validate.Length(min=2, max=80, error="First name must be between 2 and 80 characters"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="First name can only contain letters, spaces and hyphens")
    ])
    last_name = fields.Str(required=False, validate=[
        validate.Length(min=2, max=120, error="Last name must be between 2 and 120 characters"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="Last name can only contain letters, spaces and hyphens")
    ])
    plates = fields.List(fields.Str(), required=False)

update_user_schema = UpdateUserSchema()