from src.api.routes.auth import router as auth
from src.api.routes.projects import router as projects
from src.api.routes.repositories import router as repositories
from src.api.routes.metrics import router as metrics
from src.api.routes.health import router as health

__all__ = ["auth", "projects", "repositories", "metrics", "health"]
