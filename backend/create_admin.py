import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app
from app.extensions import db
from app.models.user import User
from app.schemas.user import CreateUserSchema
from marshmallow import ValidationError
import argparse

def create_admin_user(email, first_name, last_name, password):
    """Create an admin user in the database"""
    try:
        # Validate data using schema
        create_user_schema = CreateUserSchema()
        data = create_user_schema.load({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'plates': []
        })
        
        # Check if email exists
        if db.session.execute(db.select(User).filter_by(email=data['email'])).scalar():
            print("Error: Email already exists")
            return False

        # Create admin user
        admin = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
            role_id=1
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully: {email}")
        return True
        
    except ValidationError as e:
        print("Validation error:")
        for field, errors in e.messages.items():
            print(f"  {field}: {', '.join(errors)}")
        return False
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Create an admin user using command line arguments"""
    parser = argparse.ArgumentParser(description='Create an admin user')
    parser.add_argument('--email', required=True, help='Admin email')
    parser.add_argument('--first-name', required=True, help='Admin first name')
    parser.add_argument('--last-name', required=True, help='Admin last name')
    parser.add_argument('--password', required=True, help='Admin password')
    
    args = parser.parse_args()

    with app.app_context():
        create_admin_user(args.email, args.first_name, args.last_name, args.password)

if __name__ == '__main__':
    main()