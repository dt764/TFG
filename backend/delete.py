from app import db
from app.models.user import User
from app.models.role import Role
from app.models.history import History
from app.models.plate import Plate

from run import app

with app.app_context():

    # Eliminar todos los usuarios
    db.session.query(User).delete()

    # Eliminar todos los roles
    db.session.query(Role).delete()

    # Eliminar todos los historiales
    db.session.query(History).delete()

    # Eliminar todas las placas
    db.session.query(Plate).delete()

    # Confirmar los cambios en la base de datos
    db.session.commit()
