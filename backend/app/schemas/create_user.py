from marshmallow import Schema, fields, validates, ValidationError
import re

class CreateUserSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required"})
    password = fields.Str(required=True, error_messages={"required": "Password is required"})
    first_name = fields.Str(required=True, error_messages={"required": "First name is required"})
    last_name = fields.Str(required=True, error_messages={"required": "Last name is required"})
    plates = fields.List(fields.Str(), required=False, missing=[])

    @validates("password")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")

    @validates("plates")
    def validate_plates(self, value):
        if value:
            for plate in value:
                if not re.match(r'^[A-Z0-9]{6,7}$', plate):
                    raise ValidationError(f"Invalid plate format: {plate}")
                

create_user_schema = CreateUserSchema()