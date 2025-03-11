from flask import jsonify, current_app
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
import traceback
from werkzeug.exceptions import HTTPException

def register_jwt_error_handlers(jwt: JWTManager):
    @jwt.unauthorized_loader
    def custom_unauthorized_response(_err_str):
        return jsonify({"error": "Unauthorized access"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(_err_str):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(_jwt_header, _jwt_data):
        return jsonify({"error": "Token has expired"}), 401
    

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        current_app.logger.warning(f"Validation error: {err.messages}")
        return jsonify({"error": err.messages}), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(err):
        db.session.rollback()
        tb = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        current_app.logger.error(f"SQLAlchemy error: {err}\n{tb}")
        return jsonify({"error": "Database error"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        current_app.logger.warning(f"HTTP error {err.code}: {err.description}")
        return jsonify({"error": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_generic_error(err):
        tb = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        current_app.logger.error(f"Unhandled exception: {err}\n{tb}")
        return jsonify({"error": "Internal server error"}), 500
