from marshmallow import Schema, fields, validates
from ..utils.validators import validate_password

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, error_messages={"required": "Old password is required"})
    new_password = fields.Str(required=True, error_messages={"required": "New password is required"})

    @validates("new_password")
    def validate_password(self, value):
        validate_password(value)  # Llamamos a la función reutilizable
        

change_password_schema = ChangePasswordSchema()