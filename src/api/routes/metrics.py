from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.database import get_db
from src.schemas.metrics import MetricsResponse
from src.services.cache_service import CacheService
from src.services.metrics_service import MetricsService


router = APIRouter(prefix="/metrics", tags=["metrics"])


def _cache_key(prefix: str, **kwargs):
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        parts.append(f"{key}={value}")
    return ":".join(parts)


@router.get("/repository/{repo_id}", response_model=MetricsResponse)
def repository_metrics(
    repo_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    developer: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    cache = CacheService()
    key = _cache_key("repo", repo_id=repo_id, start=start_date, end=end_date, developer=developer)
    cached = cache.get_json(key)
    if cached:
        return MetricsResponse(start_date=start_date, end_date=end_date, metrics=cached)

    service = MetricsService(db)
    try:
        metrics = service.repository_metrics(repo_id, start_date, end_date, developer)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    cache.set_json(key, metrics)
    return MetricsResponse(start_date=start_date, end_date=end_date, metrics=metrics)


@router.get("/developer/{username}", response_model=MetricsResponse)
def developer_metrics(
    username: str,
    start_date: date | None = None,
    end_date: date | None = None,
    repository: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    cache = CacheService()
    key = _cache_key("dev", username=username, start=start_date, end=end_date, repo=repository)
    cached = cache.get_json(key)
    if cached:
        return MetricsResponse(start_date=start_date, end_date=end_date, metrics=cached)

    service = MetricsService(db)
    try:
        metrics = service.developer_metrics(username, start_date, end_date, repository)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    cache.set_json(key, metrics)
    return MetricsResponse(start_date=start_date, end_date=end_date, metrics=metrics)


@router.get("/project/{project_id}", response_model=MetricsResponse)
def project_metrics(
    project_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    repository: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    cache = CacheService()
    key = _cache_key(
        "project", project_id=project_id, start=start_date, end=end_date, repo=repository
    )
    cached = cache.get_json(key)
    if cached:
        return MetricsResponse(start_date=start_date, end_date=end_date, metrics=cached)

    service = MetricsService(db)
    try:
        metrics = service.project_metrics(project_id, start_date, end_date, repository)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    cache.set_json(key, metrics)
    return MetricsResponse(start_date=start_date, end_date=end_date, metrics=metrics)


@router.get("/organization", response_model=MetricsResponse)
def organization_metrics(
    start_date: date | None = None,
    end_date: date | None = None,
    repository: int | None = None,
    developer: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    cache = CacheService()
    key = _cache_key("org", start=start_date, end=end_date, repo=repository, dev=developer)
    cached = cache.get_json(key)
    if cached:
        return MetricsResponse(start_date=start_date, end_date=end_date, metrics=cached)

    service = MetricsService(db)
    metrics = service.organization_metrics(start_date, end_date, repository, developer)
    cache.set_json(key, metrics)
    return MetricsResponse(start_date=start_date, end_date=end_date, metrics=metrics)
