from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class Commit(Base, TimestampMixin):
    __tablename__ = "commits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"), index=True)
    developer_id: Mapped[int | None] = mapped_column(ForeignKey("developers.id"), index=True)
    sha: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    message: Mapped[str | None] = mapped_column(String(1000), default=None)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)

    repository = relationship("Repository", back_populates="commits")
    developer = relationship("Developer", back_populates="commits")
