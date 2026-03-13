import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.total_errors = 0
        self.total_latency = 0.0

    def record(self, latency: float, status_code: int):
        self.total_requests += 1
        self.total_latency += latency
        if status_code >= 500:
            self.total_errors += 1

    def snapshot(self):
        uptime = time.time() - self.start_time
        avg_latency = self.total_latency / self.total_requests if self.total_requests else 0.0
        error_rate = self.total_errors / self.total_requests if self.total_requests else 0.0
        return uptime, avg_latency, error_rate


metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        latency = (time.time() - start) * 1000
        metrics_collector.record(latency, response.status_code)
        return response
