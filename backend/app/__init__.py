from flask import Flask
import os

from .utils.error_handlers import register_jwt_error_handlers, register_error_handlers
from .extensions import db, bcrypt, ma, jwt, cors, migrate
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.history import history_bp
from .routes.plates import plates_bp
from .utils.middleware import middleware

from .models.role import Role
from .models.user import User

import logging


def create_roles():
    if not Role.query.filter_by(name=os.getenv("FLASK_ADMIN_ROLE")).first():
        db.session.add(Role(name=os.getenv("FLASK_ADMIN_ROLE")))
    if not Role.query.filter_by(name=os.getenv("FLASK_USER_ROLE")).first():
        db.session.add(Role(name=os.getenv("FLASK_USER_ROLE")))
    db.session.commit()

def create_admin():
    admin_email = os.getenv('FLASK_ADMIN_EMAIL')
    admin_firstname = os.getenv('FLASK_ADMIN_FIRSTNAME')
    admin_lastname = os.getenv('FLASK_ADMIN_LASTNAME')
    admin_password = os.getenv('FLASK_ADMIN_PASSWORD')
    
    existing_admin = db.session.execute(
        db.select(User).filter_by(email=admin_email)
    ).scalar_one_or_none()

    if not existing_admin:
        admin_role = db.session.execute(
            db.select(Role).filter_by(name=os.getenv('FLASK_ADMIN_ROLE'))
        ).scalar_one_or_none()

        if admin_role:
            new_admin = User(
                email=admin_email,
                first_name=admin_firstname,
                last_name=admin_lastname,
                password=admin_password,
                role_id=admin_role.id
            )
            db.session.add(new_admin)
            db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Register JWT error handlers
    register_jwt_error_handlers(jwt)

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(plates_bp)
    app.register_blueprint(middleware)

    logging.getLogger('flask_cors').level = logging.DEBUG

    return app
