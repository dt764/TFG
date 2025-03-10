import re
from marshmallow import ValidationError

def validate_password(value):
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


def validate_plate(value):
    # Validar el formato de la matrícula (6-7 caracteres, solo letras mayúsculas y números)
    if not re.match(r'^(C?\d{4}[B-DF-HJ-NP-RTV-Z]{3})$', value):
        raise ValidationError('Invalid plate format. Must be 6-7 characters long and contain only uppercase letters and numbers.')