import re
from marshmallow import ValidationError

def validate_password(value):
    # Check minimum length
    if len(value) < 8:
        raise ValidationError("La contraseña debe de tener mínimo 8 caracteres")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', value):
        raise ValidationError("La contraseña debe de tener al menos una mayúscula")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', value):
        raise ValidationError("La contraseña debe de tener al menos una minúscula")
    
    # Check for at least one number
    if not re.search(r'\d', value):
        raise ValidationError("La contraseña debe de tener al menos un número")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("La contraseña debe de tener al menos un carácter especial")


def validate_plate(value):
    # Validar el formato de la matrícula (6-7 caracteres, solo letras mayúsculas y números)
    if not re.match(r'^(C?\d{4}[B-DF-HJ-NP-RSTV-Z]{3})$', value):
        raise ValidationError('Formato inválido')