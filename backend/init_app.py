from app import create_app
from app.models.role import Role
from app.models.user import User
from app.extensions import db
import os

def create_roles():
    if not Role.query.filter_by(name=os.getenv("FLASK_ADMIN_ROLE")).first():
        db.session.add(Role(name=os.getenv("FLASK_ADMIN_ROLE")))
    if not Role.query.filter_by(name=os.getenv("FLASK_USER_ROLE")).first():
        db.session.add(Role(name=os.getenv("FLASK_USER_ROLE")))
    db.session.commit()

def create_admin():
    admin_email = os.getenv('FLASK_ADMIN_EMAIL')
    admin_firstname = os.getenv('FLASK_ADMIN_FIRSTNAME')
    admin_lastname = os.getenv('FLASK_ADMIN_LASTNAME')
    admin_password = os.getenv('FLASK_ADMIN_PASSWORD')
    
    existing_admin = db.session.execute(
        db.select(User).filter_by(email=admin_email)
    ).scalar_one_or_none()

    if not existing_admin:
        admin_role = db.session.execute(
            db.select(Role).filter_by(name=os.getenv('FLASK_ADMIN_ROLE'))
        ).scalar_one_or_none()

        if admin_role:
            new_admin = User(
                email=admin_email,
                first_name=admin_firstname,
                last_name=admin_lastname,
                password=admin_password,
                role_id=admin_role.id
            )
            db.session.add(new_admin)
            db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        create_roles()  # Crea los roles si no existen
        create_admin()  # Crea el admin si no existe
