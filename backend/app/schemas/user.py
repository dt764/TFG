from ..utils.validators import validate_password
from ..extensions import ma
from marshmallow import fields, validates, validate
from ..models.user import User
import re

class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(required=True, validate=validate.Email(error="Formato de email inválido"))
    first_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=80, error="El nombre tiene que tener entre 2 y 80 caracteres"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="El nombre solo puede tener can only letras, espacios y guiones")
    ])
    last_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=120, error="El apellido tiene que tener entre 2 y 80 caracteres"),
        validate.Regexp(r'^[a-zA-Z\s-]+$', error="El apellido solo puede tener can only letras, espacios y guiones")
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
                        error="Formato inválido.")))
    class Meta(UserSchema.Meta):
        exclude = ("id", "password_hash", "role", "histories")


class UpdateUserSchema(CreateUserSchema):
    
    class Meta(CreateUserSchema.Meta):
        exclude = ("id", "password_hash", "role", "histories", "email")

user_schema = UserSchema()
users_schema = UserSchema(many=True)
create_user_schema = CreateUserSchema(exclude=("id",))
update_user_schema = UpdateUserSchema(partial=True)  # para permitir campos opcionales
