from ..extensions import db, bcrypt
from sqlalchemy import event
import os
from .role import Role
from .plate import Plate
from .history import History

class User(db.Model):
    """User model with role support"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    role = db.relationship('Role')
    plates = db.relationship('Plate', back_populates='user', lazy=True, cascade="all, delete-orphan")
    histories = db.relationship('History', back_populates='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, email, first_name, last_name, password, role_id):
        """Initialize the user with sanitized inputs and hashed password"""
        self.email = email.strip()
        self.first_name = ' '.join(first_name.strip().split())
        self.last_name = ' '.join(last_name.strip().split())
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role_id = role_id

    def set_password(self, password):
        """Hashes and stores the user's password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifies the given password against the stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

@event.listens_for(User.__table__, 'after_create')
def create_admin(*args, **kwargs):
    admin_email = os.getenv('FLASK_ADMIN_EMAIL', 'admin@example.com')
    admin_firstname = os.getenv('FLASK_ADMIN_FIRSTNAME', 'Admin')
    admin_lastname = os.getenv('FLASK_ADMIN_LASTNAME', 'User')
    admin_password = os.getenv('FLASK_ADMIN_PASSWORD', 'admin123')
    
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role:
        db.session.add(User(
            email=admin_email,
            first_name=admin_firstname,
            last_name=admin_lastname,
            password=admin_password,
            role_id=admin_role.id
        ))
        db.session.commit()