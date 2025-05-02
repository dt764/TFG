from ..extensions import db, bcrypt
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .role import Role
from .plate import Plate
from .history import History

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(db.String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    role_id: Mapped[int] = mapped_column(db.ForeignKey('role.id'), nullable=False)

    role: Mapped[Role] = relationship()
    plates: Mapped[List["Plate"]] = relationship(back_populates="user", lazy=True, cascade="all, delete-orphan")
    histories: Mapped[List["History"]] = relationship(back_populates="user", lazy=True, cascade="all, delete-orphan")

    def __init__(self, email, first_name, last_name, password, role_id):
        self.email = email.strip()
        self.first_name = ' '.join(first_name.strip().split())
        self.last_name = ' '.join(last_name.strip().split())
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role_id = role_id

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
