from ..extensions import db
from sqlalchemy.orm import Mapped, mapped_column

class Role(db.Model):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)

