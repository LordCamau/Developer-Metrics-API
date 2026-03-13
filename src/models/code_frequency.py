from datetime import date
from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class CodeFrequencyStat(Base, TimestampMixin):
    __tablename__ = "code_frequency_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    repository = relationship("Repository", back_populates="code_frequency_stats")
