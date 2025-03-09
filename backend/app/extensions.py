from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
#from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from .utils.error_handlers import register_jwt_error_handlers

db = SQLAlchemy()
cors = CORS()
bcrypt = Bcrypt()
ma = Marshmallow()
#migrate = Migrate()
jwt = JWTManager()

# Register JWT error handlers
register_jwt_error_handlers(jwt)