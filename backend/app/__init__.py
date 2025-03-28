from flask import Flask

from .utils.error_handlers import register_jwt_error_handlers, register_error_handlers
from .extensions import db, bcrypt, ma, jwt, cors
#from .config import Config
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.history import history_bp
from .routes.plates import plates_bp
from .utils.middleware import middleware

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
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

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
