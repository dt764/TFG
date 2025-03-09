from backend import db, User, Role, app

# Create admin user
with app.app_context():

    admin_role = Role.query.filter_by(name="admin").first()  # Find admin role

    # Create and set password
    new_admin = User(
        email="admin@example.com", 
        password="admin123",
        first_name="Admin",
        last_name="User",
        role_id=admin_role.id,)

    db.session.add(new_admin)
    db.session.commit()
