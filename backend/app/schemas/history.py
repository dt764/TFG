from ..utils.validators import validate_plate
from ..extensions import ma
from marshmallow import Schema, fields, validates
from .plate import PlateSchema
from .user import UserSchema
from ..models.history import History
from datetime import datetime

class HistorySchema(ma.SQLAlchemyAutoSchema):
    registered_plate = fields.Nested(lambda: PlateSchema(only=("plate",)))
    user = fields.Nested(lambda: UserSchema(only=("id", "first_name", "last_name", "email")))

    class Meta:
        model = History
        include_fk = True

class VerifyPlateRequestSchema(Schema):
    plate = fields.Str(required=True)
    date = fields.DateTime(
        format='%Y-%m-%dT%H:%M:%SZ',
        missing=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    )

    @validates('plate')
    def validate_plate_field(self, value):
        validate_plate(value)

class VerifyPlateResponseSchema(Schema):
    allowed = fields.Boolean(required=True)
    plate = fields.Str(required=True)
    registered = fields.Boolean(required=True)
    user = fields.Nested('UserSchema', dump_only=True, only=('id', 'email', 'first_name', 'last_name'))

history_schema = HistorySchema()
histories_schema = HistorySchema(many=True)
verify_plate_request_schema = VerifyPlateRequestSchema()
verify_plate_response_schema = VerifyPlateResponseSchema()
