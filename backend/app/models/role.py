from ..extensions import db
from sqlalchemy import event
import os

class Role(db.Model):
    """Role model to distinguish between normal users and administrators"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

@event.listens_for(Role.__table__, 'after_create')
def create_roles(*args, **kwargs):
    """Create initial roles after Role table is created"""
    admin_role = os.getenv('FLASK_ADMIN_ROLE', 'admin')
    user_role = os.getenv('FLASK_USER_ROLE', 'user')
    
    db.session.add(Role(name=admin_role))
    db.session.add(Role(name=user_role))
    db.session.commit()