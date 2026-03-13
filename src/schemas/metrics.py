from datetime import date
from pydantic import BaseModel


class MetricsResponse(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    metrics: dict
