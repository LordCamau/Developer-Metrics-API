from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class Deployment(Base, TimestampMixin):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), index=True)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    environment: Mapped[str | None] = mapped_column(String(100), default=None)
    status: Mapped[str | None] = mapped_column(String(50), default=None)
    description: Mapped[str | None] = mapped_column(String(500), default=None)

    repository = relationship("Repository", back_populates="deployments")
