from ..extensions import db
import re

class Plate(db.Model):
    """Vehicle plate model linked to a user"""
    plate = db.Column(db.String(20), primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='plates')

    def __init__(self, plate, user):
        if not re.match(r'^[A-Z0-9]{6,7}$', plate):  # Plate format validation
            raise ValueError("Invalid plate format")
        self.plate = plate
        self.user = user