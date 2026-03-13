from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    APP_NAME: str = "Developer Metrics API"
    ENV: str = "development"

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/devmetrics"
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_ENABLED: bool = True

    GITHUB_TOKEN: str | None = None

    CACHE_TTL_SECONDS: int = 300
    RATE_LIMIT_REQUESTS: int = 200
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    WORKER_SYNC_INTERVAL_SECONDS: int = 900
    WORKER_METRICS_INTERVAL_SECONDS: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
