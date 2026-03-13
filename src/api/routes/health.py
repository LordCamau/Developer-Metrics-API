from fastapi import APIRouter

from src.middleware.metrics import metrics_collector
from src.schemas.health import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    uptime, avg_latency, error_rate = metrics_collector.snapshot()
    return HealthResponse(
        status="ok",
        uptime_seconds=uptime,
        avg_latency_ms=avg_latency,
        error_rate=error_rate,
    )
