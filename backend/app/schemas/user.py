from ..extensions import ma
from marshmallow import fields, validates, ValidationError, validate
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
        # Check minimum length
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        # Check for at least one number
        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one number")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character")

user_schema = UserSchema()
users_schema = UserSchema(many=True)