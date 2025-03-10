from flask import jsonify, current_app
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db

def register_jwt_error_handlers(jwt: JWTManager):
    @jwt.unauthorized_loader
    def custom_unauthorized_response(_err_str):
        return jsonify({"error": "Acceso no autorizado"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(_err_str):
        return jsonify({"error": "Token inválido"}), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(_jwt_header, _jwt_data):
        return jsonify({"error": "Token expirado"}), 401
    

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"error": err.messages}), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(err):
        db.session.rollback()
        current_app.logger.error(f"SQLAlchemy error: {str(err)}")
        return jsonify({"error": "Database error"}), 500

    @app.errorhandler(Exception)
    def handle_generic_error(err):
        current_app.logger.error(f"Unhandled exception: {str(err)}")
        return jsonify({"error": "Internal server error"}), 500
