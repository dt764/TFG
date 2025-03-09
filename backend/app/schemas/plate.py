from ..extensions import ma
from ..models.plate import Plate
from marshmallow import fields, validates, ValidationError
import re

class PlateSchema(ma.SQLAlchemyAutoSchema):
    plate = fields.Str(required=True)

    class Meta:
        model = Plate
        include_fk = True

    @validates('plate')
    def validate_plate(self, value):
        # Validate plate format (6-7 characters, only uppercase letters and numbers)
        if not re.match(r'^(C?\d{4}[B-DF-HJ-NP-RTV-Z]{3})$', value):
            raise ValidationError('Invalid plate format. Must be 6-7 characters long and contain only uppercase letters and numbers.')

plate_schema = PlateSchema()
plates_schema = PlateSchema(many=True)