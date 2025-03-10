from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.plate import Plate
from ..schemas.user import user_schema, users_schema, create_user_schema, update_user_schema
from ..utils.auth_utils import role_required

users_bp = Blueprint('users', __name__)

#---------------------------------#

@users_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users():

    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify(users_schema.dump(users)), 200

#---------------------------------#

@users_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():

    json_data = request.get_json()
    create_user_schema.validate(json_data)

    data = create_user_schema.load(json_data)

    # Check if email exists
    if db.session.execute(db.select(User).filter_by(email=data['email'])).scalar():
        return jsonify({"error": "Email already exists"}), 400

    # Check if any plate already exists
    existing_plates = [
        plate_number for plate_number in data.get('plates', [])
        if db.session.execute(db.select(Plate).filter_by(plate=plate_number)).scalar()
    ]
    if existing_plates:
        return jsonify({
            "error": "The following plates are already registered",
            "plates": existing_plates
        }), 400

    new_user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=data['password'],
        role_id=2  # Usuario normal
    )

    # Add plates if any
    for plate_number in data.get('plates', []):
        db.session.add(Plate(plate=plate_number, user=new_user))

    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user)), 201

#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if current_user.role.name == "user" and current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200

#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['PUT'], endpoint="update_user")
@jwt_required()
@role_required('admin')
def update_user(user_id):
    json_data = request.get_json()
    update_user_schema.validate(json_data)

    data = update_user_schema.load(json_data)
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if 'email' in data and data['email'] != user.email:
        if db.session.execute(db.select(User).filter_by(email=data['email'])).scalar():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']

    if 'plates' in data:
        existing_plates = [
            # Check if any plate already exists with another user
            plate_number for plate_number in data['plates']
            if (plate := db.session.execute(db.select(Plate).filter_by(plate=plate_number)).scalar())
            and plate.user_id != user_id
        ]
        if existing_plates:
            return jsonify({
                "error": "The following plates are already registered",
                "plates": existing_plates
            }), 400

        db.session.execute(db.delete(Plate).where(Plate.user_id == user_id))
        for plate_number in data['plates']:
            db.session.add(Plate(plate=plate_number, user=user))

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['DELETE'], endpoint="delete_user")
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."}), 200
