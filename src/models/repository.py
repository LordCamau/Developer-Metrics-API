from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


repository_developers = Table(
    "repository_developers",
    Base.metadata,
    Column("repository_id", ForeignKey("repositories.id"), primary_key=True),
    Column("developer_id", ForeignKey("developers.id"), primary_key=True),
)


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    repo_url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    owner: Mapped[str] = mapped_column(String(200), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    default_branch: Mapped[str | None] = mapped_column(String(100), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    project = relationship("Project", back_populates="repositories")
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="repository", cascade="all, delete-orphan")
    developers = relationship("Developer", secondary=repository_developers, back_populates="repositories")
    code_frequency_stats = relationship(
        "CodeFrequencyStat", back_populates="repository", cascade="all, delete-orphan"
    )
