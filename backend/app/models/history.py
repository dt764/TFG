from ..extensions import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

class History(db.Model):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    plate: Mapped[str] = mapped_column(db.String(20), nullable=False)
    date: Mapped[str] = mapped_column(db.String(25), nullable=False, default=lambda: datetime.utcnow().isoformat() + "Z")
    user_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('user.id'), nullable=True)
    allowed: Mapped[bool] = mapped_column(nullable=False)

    registered_plate: Mapped["Plate"] = relationship('Plate', primaryjoin="History.plate==Plate.plate", foreign_keys=[plate], viewonly=True)
    user: Mapped["User"] = relationship(back_populates='histories')
