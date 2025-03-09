from flask import jsonify
from flask_jwt_extended import JWTManager

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