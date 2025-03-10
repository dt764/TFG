from ..utils.validators import validate_password
from ..extensions import ma
from marshmallow import fields, validates, validate
from ..models.user import User
import re

class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(required=True, validate=validate.Email(error="Invalid email format"))
    first_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=80, error="First name must be between 2 and 80 characters"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="First name can only contain letters, spaces and hyphens")
    ])
    last_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=120, error="Last name must be between 2 and 120 characters"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="Last name can only contain letters, spaces and hyphens")
    ])
    password = fields.Str(load_only=True, required=True)
    plates = fields.Method("get_plates")

    class Meta:
        model = User
        exclude = ("password_hash", "role", "histories")
        include_relationships = True

    def get_plates(self, obj):
        return [plate.plate for plate in obj.plates]

    @validates("password")
    def validate_password(self, value):
        validate_password(value)  # Llamamos a la función reutilizable
        

class CreateUserSchema(UserSchema):
    plates = fields.List(fields.Str(validate=validate.Regexp(r'^(C?\d{4}[B-DF-HJ-NP-RTV-Z]{3})$', 
                        error="Invalid plate format. Plates must be 6-7 characters long and contain only uppercase letters and numbers.")))
    class Meta(UserSchema.Meta):
        exclude = ("id", "password_hash", "role", "histories")

user_schema = UserSchema()
users_schema = UserSchema(many=True)
create_user_schema = CreateUserSchema(exclude=("id",))
update_user_schema = UserSchema(partial=True)  # para permitir campos opcionales
