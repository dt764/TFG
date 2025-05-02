from ..extensions import db
from ..models.plate import Plate
from ..models.history import History
from ..schemas.history import histories_schema
from flask import Blueprint, request, jsonify
from ..utils.auth_utils import check_api_key, role_required
from ..schemas.history import verify_plate_request_schema, verify_plate_response_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User

import os

history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
@jwt_required()
@role_required(os.getenv("FLASK_ADMIN_ROLE"))
def get_history():
    history_records = db.session.execute(db.select(History)).scalars().all()
    return jsonify(histories_schema.dump(history_records)), 200

@history_bp.route('/verify_plate', methods=['POST'])
def verify_plate():
    if not check_api_key(request):
        return jsonify({"error": "Unauthorized. Invalid API_KEY."}), 403
    
    # Validate request data
    verify_plate_request_schema.validate(request.get_json())
        
    data = verify_plate_request_schema.load(request.get_json())
    
    # Check if plate is registered
    plate_obj = db.session.execute(db.select(Plate).where(Plate.plate == data['plate'])).scalar_one_or_none()
    is_registered = bool(plate_obj)

    # Create history record
    new_history = History(
        plate=data['plate'],
        date=data['date'],
        allowed=is_registered,
        user_id=plate_obj.user_id if plate_obj else None
    )
    db.session.add(new_history)
    db.session.commit()

    # Prepare response
    response_data = {
        "allowed": is_registered,
        "plate": data['plate']
    }
    
    if plate_obj:
        response_data["user"] = plate_obj.user

    return jsonify(verify_plate_response_schema.dump(response_data)), 200
            

@history_bp.route('/users/<int:user_id>/history', methods=['GET'])
@jwt_required()
def get_user_history(user_id):
        
    # Get current user from JWT
    current_user_id = get_jwt_identity()
    current_user = db.session.execute(db.select(User).where(User.id == current_user_id)).scalar_one_or_none()
    
    # Check if user exists
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Only admins can see other users' history
    if current_user.role.name != "admin" and current_user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
        
    # Get history records for the user
    history_records = db.session.execute(db.select(History).where(History.user_id == user_id)).scalars().all()
    return jsonify(histories_schema.dump(history_records)), 200
