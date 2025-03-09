from ..extensions import db
from datetime import datetime

class History(db.Model):
    """History model to store access records"""
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(25), nullable=False, default=lambda: datetime.utcnow().isoformat() + "Z")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    allowed = db.Column(db.Boolean, nullable=False)

    # Optional relationship with Plate model
    registered_plate = db.relationship('Plate', primaryjoin="History.plate==Plate.plate", foreign_keys=[plate])
    user = db.relationship('User')