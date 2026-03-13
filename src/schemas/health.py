from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    avg_latency_ms: float
    error_rate: float
