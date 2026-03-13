from fastapi import FastAPI
from dotenv import load_dotenv

from src.api.routes import auth, health, metrics, projects, repositories
from src.core.config import get_settings
from src.middleware.metrics import MetricsMiddleware
from src.middleware.rate_limit import RateLimitMiddleware


load_dotenv()
settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(repositories.router)
app.include_router(metrics.router)
app.include_router(health.router)
