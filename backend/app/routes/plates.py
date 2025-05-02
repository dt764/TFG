from flask import Blueprint, jsonify
import os
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.plate import Plate
from ..schemas.plate import plates_schema
from ..utils.auth_utils import role_required

plates_bp = Blueprint('plates', __name__)

@plates_bp.route('/plates', methods=['GET'])
@jwt_required()
@role_required(os.getenv("FLASK_ADMIN_ROLE"))
def get_plates():
    """Get all plates (admin only)"""
    plates = db.session.execute(db.select(Plate)).scalars().all()
    return jsonify(plates_schema.dump(plates)), 200


