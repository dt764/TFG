import os
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from ..models.user import User

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
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
    return api_key == os.getenv('FLASK_API_KEY')
