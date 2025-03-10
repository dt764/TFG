from ..extensions import db
from sqlalchemy import event
import os
from sqlalchemy.orm import Mapped, mapped_column

class Role(db.Model):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)

@event.listens_for(Role.__table__, 'after_create')
def create_roles(*args, **kwargs):
    admin_role = os.getenv('FLASK_ADMIN_ROLE', 'admin')
    user_role = os.getenv('FLASK_USER_ROLE', 'user')
    
    db.session.add_all([
        Role(name=admin_role),
        Role(name=user_role)
    ])
    db.session.commit()
