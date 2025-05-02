from flask import Blueprint, jsonify, request
import os
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.plate import Plate
from ..models.role import Role
from ..schemas.user import user_schema, users_schema, create_user_schema, update_user_schema
from ..utils.auth_utils import role_required


users_bp = Blueprint('users', __name__)

user_role_name = os.getenv('FLASK_USER_ROLE')
admin_role_name = os.getenv('FLASK_ADMIN_ROLE')

def get_user_role_id():
    # Get the user role ID from the database
    # This function assumes that the user role is already present in the database
    stmt = db.select(Role).where(Role.name == user_role_name)
    user_role = db.session.execute(stmt).scalar()
    return user_role.id

def get_admin_role_id():
    # Get the admin role ID from the database
    # This function assumes that the admin role is already present in the database
    stmt = db.select(Role).where(Role.name == admin_role_name)
    admin_role = db.session.execute(stmt).scalar()
    return admin_role.id
    

#---------------------------------#

@users_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required(admin_role_name)
def get_users():
    # Select users where role_id is not 1 (admin)
    user_role_id = get_user_role_id()
    stmt = db.select(User).where(User.role_id == user_role_id)
    users = db.session.execute(stmt).scalars().all()
    return jsonify(users_schema.dump(users)), 200

#---------------------------------#

@users_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required(admin_role_name)
def create_user():
    json_data = request.get_json()

    # Validación del esquema
    errors = create_user_schema.validate(json_data)
    if errors:
        return jsonify({"error": errors}), 400

    data = create_user_schema.load(json_data)
    plates = data.get('plates', [])

    error_response = {}
    plate_indices_map = {}
    plate_errors_by_index = {}

    # Detectar duplicados en el payload
    for index, plate in enumerate(plates):
        if plate in plate_indices_map:
            first_index = plate_indices_map[plate]
            if str(first_index) not in plate_errors_by_index:
                plate_errors_by_index[str(first_index)] = ["Duplicado"]
            plate_errors_by_index[str(index)] = ["Duplicado"]
        else:
            plate_indices_map[plate] = index

    # Verificar placas ya registradas en la base de datos
    existing_plates = db.session.execute(
        db.select(Plate.plate).filter(Plate.plate.in_(plates))
    ).scalars().all()

    # Marcar los índices de las placas existentes
    for index, plate in enumerate(plates):
        if plate in existing_plates:
            if str(index) not in plate_errors_by_index:
                plate_errors_by_index[str(index)] = []
            plate_errors_by_index[str(index)].append("Ya registrada en la base de datos")

    if plate_errors_by_index:
        error_response["plates"] = plate_errors_by_index

    # Verificar si el correo ya existe
    if db.session.execute(db.select(User).filter_by(email=data['email'])).scalar():
        error_response["email"] = ["Email ya registrado"]

    # Si hay errores, devolverlos todos juntos
    if error_response:
        return jsonify({"error": error_response}), 400

    # Crear usuario
    new_user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=data['password'],  # Recuerda hashear
        role_id=get_user_role_id() # Rol de usuario normal
    )

    # Asociar placas
    for plate_number in plates:
        db.session.add(Plate(plate=plate_number, user=new_user))

    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user)), 201


#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if current_user.role.name == user_role_name and current_user.id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200

#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['PUT'], endpoint="update_user")
@jwt_required()
@role_required(admin_role_name)
def update_user(user_id):
    json_data = request.get_json()
    update_user_schema.validate(json_data)

    data = update_user_schema.load(json_data)
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role.id == 1:
        return jsonify({"error": "Cannot modify admin users"}), 403

    error_response = {}

    # Campos personales
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']

    # Validar y actualizar placas
    if 'plates' in data:
        plates = data['plates']
        plate_indices_map = {}
        plate_errors_by_index = {}

        # Duplicados en el payload
        for index, plate in enumerate(plates):
            if plate in plate_indices_map:
                first_index = plate_indices_map[plate]
                if str(first_index) not in plate_errors_by_index:
                    plate_errors_by_index[str(first_index)] = ["Duplicado"]
                plate_errors_by_index[str(index)] = ["Duplicado"]
            else:
                plate_indices_map[plate] = index

        # Placas registradas por otro usuario
        plates_to_check = set(plates)
        if plates_to_check:
            existing_plates = db.session.execute(
                db.select(Plate).filter(Plate.plate.in_(plates_to_check))
            ).scalars().all()

            for existing_plate in existing_plates:
                if existing_plate.user_id != user_id:
                    for index, plate in enumerate(plates):
                        if plate == existing_plate.plate:
                            if str(index) not in plate_errors_by_index:
                                plate_errors_by_index[str(index)] = []
                            plate_errors_by_index[str(index)].append("Ya registrada en otro usuario")

        if plate_errors_by_index:
            error_response["plates"] = plate_errors_by_index

    if error_response:
        return jsonify({"error": error_response}), 400

    # Si no hay errores, actualizar placas
    if 'plates' in data:
        db.session.execute(db.delete(Plate).where(Plate.user_id == user_id))
        for plate_number in set(data['plates']):
            db.session.add(Plate(plate=plate_number, user=user))

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200


#---------------------------------#

@users_bp.route('/users/<int:user_id>', methods=['DELETE'], endpoint="delete_user")
@jwt_required()
@role_required(admin_role_name)
def delete_user(user_id):
    user = db.session.get(User, user_id)

    # Check if the user is an admin
    if user.role.name == admin_role_name:
        return jsonify({"error": "Cannot delete admin users"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."}), 200
