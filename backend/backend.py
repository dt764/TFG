from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import datetime, timedelta, timezone
import re
import logging
import os

from marshmallow import post_dump

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Obtiene el directorio del script
DB_PATH = os.path.join(BASE_DIR, "database.db")  # Construye el path absoluto


# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['API_KEY'] = 'your-secret-api-key'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)




# ------------- MODELS -------------

class Role(db.Model):
    """Role model to distinguish between normal users and administrators"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)




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



class History(db.Model):
    """History model to store access records"""
    plate_id = db.Column(db.String(20), db.ForeignKey('plate.plate'), primary_key=True)
    date = db.Column(db.String(25), primary_key=True, default=lambda: datetime.utcnow().isoformat() + "Z")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  
    allowed = db.Column(db.Boolean, nullable=False)

    plate = db.relationship('Plate')
    user = db.relationship('User')





# ------------- SCHEMAS (MARSHMALLOW) -------------

class PlateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Plate
        include_fk = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    plates = ma.List(ma.String())  # Returns only plate numbers
    class Meta:
        model = User

    @post_dump
    def simplify_plates(self, data, **kwargs):
        data['plates'] = [plate['plate'] for plate in data.get('plates', [])]
        return data

class HistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = History
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
plate_schema = PlateSchema()
history_schema = HistorySchema(many=True)




# ------------- HELPER FUNCTIONS -------------

def role_required(required_role):
    """Decorator to restrict access based on user role"""
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if not current_user or current_user.role.name != required_role:
                return jsonify({"error": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def check_api_key(request):
    """Validates the API key in the request headers"""
    api_key = request.headers.get('API_KEY')
    return api_key == app.config['API_KEY']


# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response





# ------------- AUTHENTICATION ENDPOINTS -------------

@app.route('/register', methods=['POST'])
@role_required('admin')
def register():
    """Registers a new normal user"""
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    user_role = Role.query.filter_by(name="user").first()
    new_user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role_id=user_role.id
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Authenticates a user and returns a JWT token"""
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(user_schema.dump(user))
        set_access_cookies(response, access_token)
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response



# ------------- USER ENDPOINTS -------------

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Allows users to get their own data, or admins to get any user"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if current_user.role.name == "user" and current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200

@app.route('/users', methods=['GET'], endpoint="get_users")
@role_required('admin')
def get_users():
    """Allows only admins to get all users"""
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200

@app.route('/users/<int:user_id>', methods=['PUT'], endpoint="update_user")
@role_required('admin')
def update_user(user_id):
    """Allows only admins to modify user data"""
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.email = data.get('email', user.email)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

@app.route('/users/<int:user_id>', methods=['DELETE'],  endpoint="delete_user")
@role_required('admin')
def delete_user(user_id):
    """Allows only admins to delete users"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."}), 200


# ------------- HISTORY ENDPOINT -------------

@app.route('/verify_plate', methods=['POST'])
def verify_plate():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized. Invalid API_KEY."}), 403
    
    data = request.get_json()
    plate_number = data.get('plate')
    date = data.get('date', datetime.utcnow().isoformat() + "Z")

    plate = Plate.query.filter_by(plate=plate_number).first()

    new_history = History(
        plate_id=plate_number,
        date=date,
        allowed=bool(plate),
        user_id=plate.user_id if plate else None
    )
    db.session.add(new_history)
    db.session.commit()

    if plate:
        return jsonify({"allowed": True, "plate": plate_number, "user": user_schema.dump(plate.user)}), 200
    else:
        return jsonify({"allowed": False, "plate": plate_number}), 200



# ------------- DATABASE INITIALIZATION -------------
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print("Base de datos usada:", app.config["SQLALCHEMY_DATABASE_URI"])
    with app.app_context():
        db.create_all()
        if not Role.query.filter_by(name="admin").first():
            db.session.add(Role(name="admin"))
            db.session.add(Role(name="user"))
            db.session.commit()
    app.run(debug=True)
