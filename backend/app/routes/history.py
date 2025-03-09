from ..extensions import db
from ..models.plate import Plate
from ..models.history import History
from ..schemas.user import user_schema
from ..schemas.history import history_schema, histories_schema
from flask import Blueprint, request, jsonify, current_app
from ..utils.auth_utils import check_api_key
from ..schemas.history import verify_plate_request_schema, verify_plate_response_schema
import traceback

history_bp = Blueprint('veirfy_plate', __name__)

@history_bp.route('/history', methods=['GET'])
def get_history():
    history_records = History.query.all()
    history_list = histories_schema.dump(history_records, many=True)
    return jsonify(history_list), 200

@history_bp.route('/verify_plate', methods=['POST'])
def verify_plate():
    try:
        if not check_api_key(request):
            return jsonify({"error": "Unauthorized. Invalid API_KEY."}), 403
        
        # Validate request data
        errors = verify_plate_request_schema.validate(request.get_json())
        if errors:
            return jsonify({"error": errors}), 400
            
        data = verify_plate_request_schema.load(request.get_json())
        
        # Check if plate is registered
        plate_obj = Plate.query.filter_by(plate=data['plate']).first()
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
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error verifying plate: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}")
        return jsonify({"error": "Internal server error"}), 500
