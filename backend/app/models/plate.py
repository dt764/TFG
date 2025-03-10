from ..extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Plate(db.Model):
    __tablename__ = "plate"

    plate: Mapped[str] = mapped_column(db.String(20), primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="plates")

