from ..utils.validators import validate_plate
from ..extensions import ma
from ..models.plate import Plate
from marshmallow import fields, validates

class PlateSchema(ma.SQLAlchemyAutoSchema):
    plate = fields.Str(required=True)

    class Meta:
        model = Plate
        include_fk = True

    @validates('plate')
    @validates('plate')
    def validate_plate_field(self, value):
        validate_plate(value)

plate_schema = PlateSchema()
plates_schema = PlateSchema(many=True)