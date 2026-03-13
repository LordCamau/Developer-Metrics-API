from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class PullRequest(Base, TimestampMixin):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), index=True)
    developer_id: Mapped[int | None] = mapped_column(ForeignKey("developers.id"), index=True)
    number: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str | None] = mapped_column(String(500), default=None)
    state: Mapped[str] = mapped_column(String(50), index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    repository = relationship("Repository", back_populates="pull_requests")
    developer = relationship("Developer", back_populates="pull_requests")
