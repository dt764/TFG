from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from ..models.user import User
from ..schemas.user import user_schema
from ..schemas.change_password import change_password_schema
from ..extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(user_schema.dump(user))
        set_access_cookies(response, access_token)
        return response
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        # Validate request data using schema
        errors = change_password_schema.validate(request.get_json())
        if errors:
            return jsonify({"error": errors}), 400
            
        data = change_password_schema.load(request.get_json())
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if not user.check_password(data['old_password']):
            return jsonify({"error": "Current password is incorrect"}), 401
            
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        # Create new response and remove old token
        response = jsonify({"message": "Password changed successfully"})
        unset_jwt_cookies(response)
        
        return response
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while changing password"}), 500