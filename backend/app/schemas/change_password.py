from marshmallow import Schema, fields, validates, ValidationError

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, error_messages={"required": "Old password is required"})
    new_password = fields.Str(required=True, error_messages={"required": "New password is required"})

    @validates("new_password")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        

change_password_schema = ChangePasswordSchema()