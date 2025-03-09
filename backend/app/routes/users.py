from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.plate import Plate
from ..schemas.user import user_schema, users_schema
from ..utils.auth_utils import role_required
from ..schemas.create_user import create_user_schema
from ..schemas.update_user import update_user_schema
import traceback

users_bp = Blueprint('users', __name__)


#---------------------------------#

@users_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users)), 200



#---------------------------------#

@users_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    try:
        # Validate request data
        errors = create_user_schema.validate(request.get_json())
        if errors:
            return jsonify({"error": errors}), 400
            
        data = create_user_schema.load(request.get_json())
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        
        # Check if any plate already exists
        existing_plates = []
        for plate_number in data.get('plates', []):
            if Plate.query.filter_by(plate=plate_number).first():
                existing_plates.append(plate_number)
        
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
            role_id=2  # Assuming 2 is the user role ID
        )
        
        # Add plates if any
        for plate_number in data.get('plates', []):
            plate = Plate(plate=plate_number, user=new_user)
            db.session.add(plate)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(user_schema.dump(new_user)), 201
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}")
        return jsonify({"error": "Internal server error"}), 500



#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if current_user.role.name == "user" and current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200



#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['PUT'], endpoint="update_user")
@jwt_required()
@role_required('admin')
def update_user(user_id):
    try:
        # Validate request data
        errors = update_user_schema.validate(request.get_json())
        if errors:
            return jsonify({"error": errors}), 400
            
        data = update_user_schema.load(request.get_json())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if email exists and it's not the same user
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({"error": "Email already exists"}), 400
            user.email = data['email']

        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        # Update plates if provided
        if 'plates' in data:
            # Check if any plate already exists with another user
            existing_plates = []
            for plate_number in data['plates']:
                plate = Plate.query.filter_by(plate=plate_number).first()
                if plate and plate.user_id != user_id:
                    existing_plates.append(plate_number)
            
            if existing_plates:
                return jsonify({
                    "error": "The following plates are already registered",
                    "plates": existing_plates
                }), 400

            # Remove existing plates
            Plate.query.filter_by(user_id=user_id).delete()
            
            # Add new plates
            for plate_number in data['plates']:
                plate = Plate(plate=plate_number, user=user)
                db.session.add(plate)

        db.session.commit()
        return jsonify(user_schema.dump(user)), 200
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}")
        return jsonify({"error": "Internal server error"}), 500


#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['DELETE'],  endpoint="delete_user")
@role_required('admin')
def delete_user(user_id):
    """Allows only admins to delete users"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."}), 200
