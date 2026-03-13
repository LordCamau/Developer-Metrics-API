from sqlalchemy.orm import Session

from src.models.metrics_snapshot import MetricsSnapshot


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_snapshot(self, snapshot: MetricsSnapshot) -> MetricsSnapshot:
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot
