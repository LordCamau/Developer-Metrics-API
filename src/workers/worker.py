from apscheduler.schedulers.blocking import BlockingScheduler

from src.core.config import get_settings
from src.core.database import SessionLocal
from src.repositories.repository_repo import RepositoryRepository
from src.services.aggregation_service import AggregationService
from src.services.repository_service import RepositoryService


settings = get_settings()


def sync_repositories():
    db = SessionLocal()
    try:
        repo_repo = RepositoryRepository(db)
        service = RepositoryService(db)
        for repo in repo_repo.list_all():
            try:
                service.sync_repository(repo)
            except Exception:
                db.rollback()
    finally:
        db.close()


def aggregate_metrics():
    db = SessionLocal()
    try:
        AggregationService(db).snapshot_all_repositories()
    finally:
        db.close()


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(sync_repositories, "interval", seconds=settings.WORKER_SYNC_INTERVAL_SECONDS)
    scheduler.add_job(
        aggregate_metrics, "interval", seconds=settings.WORKER_METRICS_INTERVAL_SECONDS
    )
    scheduler.start()


if __name__ == "__main__":
    main()
