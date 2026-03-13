from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class MetricsSnapshot(Base, TimestampMixin):
    __tablename__ = "metrics_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, default=None)
    repository_id: Mapped[int | None] = mapped_column(ForeignKey("repositories.id"), index=True, default=None)
    developer_id: Mapped[int | None] = mapped_column(ForeignKey("developers.id"), index=True, default=None)
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    metrics: Mapped[dict] = mapped_column(JSON)
