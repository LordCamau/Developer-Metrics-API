from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class Developer(Base, TimestampMixin):
    __tablename__ = "developers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)

    repositories = relationship("Repository", secondary="repository_developers", back_populates="developers")
    commits = relationship("Commit", back_populates="developer", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="developer", cascade="all, delete-orphan")
