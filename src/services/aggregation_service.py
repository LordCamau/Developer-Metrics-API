from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.models.metrics_snapshot import MetricsSnapshot
from src.models.repository import Repository
from src.repositories.metrics_repo import MetricsRepository
from src.services.metrics_service import MetricsService


class AggregationService:
    def __init__(self, db: Session):
        self.db = db
        self.metrics = MetricsService(db)
        self.snapshots = MetricsRepository(db)

    def snapshot_repository_metrics(self, repository_id: int, start_date: date, end_date: date):
        metrics = self.metrics.repository_metrics(repository_id, start_date=start_date, end_date=end_date)
        snapshot = MetricsSnapshot(
            repository_id=repository_id,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics,
        )
        return self.snapshots.create_snapshot(snapshot)

    def snapshot_all_repositories(self):
        today = date.today()
        start_date = today - timedelta(days=1)
        repos = self.db.query(Repository).all()
        for repo in repos:
            self.snapshot_repository_metrics(repo.id, start_date, today)
