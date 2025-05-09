from flask import Blueprint, request, jsonify
import os
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from ..models.user import User
from ..models.role import Role
from ..schemas.user import user_schema
from ..schemas.change_password import change_password_schema
from ..extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def user_login():
    data = request.get_json()
    user = db.session.query(User).filter_by(email=data['email']).first()
    user_role_id = db.session.query(Role).filter_by(name=os.getenv("FLASK_USER_ROLE")).first().id

    if user and user.check_password(data['password']):
        if user.role_id != user_role_id:
            return jsonify({"error": "Access denied"}), 403
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(user_schema.dump(user))
        set_access_cookies(response, access_token)
        return response

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    user = db.session.query(User).filter_by(email=data['email']).first()
    admin_role_id = db.session.query(Role).filter_by(name=os.getenv("FLASK_ADMIN_ROLE")).first().id

    if user and user.check_password(data['password']):
        if user.role_id != admin_role_id:
            return jsonify({"error": "Access denied"}), 403
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
    # Validate the request data using the schema
    change_password_schema.validate(request.get_json())

    data = change_password_schema.load(request.get_json())
    current_user_id = get_jwt_identity()
    
    # Get the current user using db.session
    user = db.session.query(User).get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the current password is correct
    if not user.check_password(data['old_password']):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Update the password within a transaction
    user.set_password(data['new_password'])
    
    # Commit the changes to the database
    db.session.commit()

    # Create a new response and remove the old token
    response = jsonify({"message": "Password changed successfully"})
    unset_jwt_cookies(response)

    return response


@auth_bp.route("/check-user-session", methods=["GET"])
@jwt_required()
def check_user_session():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_role = db.session.query(Role).filter_by(name=os.getenv("FLASK_USER_ROLE")).first()
    if not user_role:
        return jsonify({"error": "User role not configured"}), 500

    if user.role_id != user_role.id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify({"msg": "Valid user session"}), 200


@auth_bp.route("/check-admin-session", methods=["GET"])
@jwt_required()
def check_admin_session():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    admin_role = db.session.query(Role).filter_by(name=os.getenv("FLASK_ADMIN_ROLE")).first()
    if not admin_role:
        return jsonify({"error": "Admin role not configured"}), 500

    if user.role_id != admin_role.id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify({"msg": "Valid admin session"}), 200

