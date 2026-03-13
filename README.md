# Developer Metrics API

Engineering analytics backend that ingests GitHub repository activity and exposes productivity metrics for teams.

**Tech stack:** FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, Docker, Pytest.

## Architecture

Clean architecture layout:

- `src/api`: FastAPI routes and dependencies
- `src/core`: config, database, security
- `src/models`: SQLAlchemy models
- `src/schemas`: Pydantic request/response models
- `src/repositories`: data access layer
- `src/services`: business logic (auth, GitHub sync, metrics)
- `src/middleware`: rate limiting + metrics
- `src/workers`: background scheduler
- `src/utils`: helpers

## Database Schema

Core tables:

- `users`
- `projects`
- `repositories`
- `developers`
- `commits`
- `pull_requests`
- `deployments`
- `metrics_snapshots`
- `code_frequency_stats` (GitHub code frequency data)

Relationships:

- `projects.owner_id -> users.id`
- `repositories.project_id -> projects.id`
- `commits.repository_id -> repositories.id`
- `pull_requests.repository_id -> repositories.id`
- `deployments.repository_id -> repositories.id`
- `metrics_snapshots` optional foreign keys to project/repo/developer
- `repository_developers` many-to-many between repositories and developers

## API Endpoints

**Auth**
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

**Projects**
- `POST /projects`
- `GET /projects`
- `GET /projects/{id}`
- `DELETE /projects/{id}`

**Repositories**
- `POST /repositories/connect`
- `GET /repositories`
- `POST /repositories/{id}/sync`

**Metrics**
- `GET /metrics/repository/{repo_id}`
- `GET /metrics/developer/{username}`
- `GET /metrics/project/{project_id}`
- `GET /metrics/organization`

**Health**
- `GET /health`

### Filters

Metrics endpoints support:

- `start_date` (YYYY-MM-DD)
- `end_date` (YYYY-MM-DD)
- `developer` (for repository metrics)
- `repository` (scopes developer/project/org metrics to a repository)

## Local Development

From `backend/`:

```bash
cp .env.example .env

docker-compose up --build
```

Run migrations:

```bash
docker-compose exec api alembic upgrade head
```

Seed sample data:

```bash
docker-compose exec api python seed_data.py
```

Run tests locally:

```bash
pytest
```

## Example curl

Register/login:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","username":"dev1","password":"password123"}'
```

Create a project:

```bash
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Platform","description":"Core services"}'
```

Connect a repo:

```bash
curl -X POST http://localhost:8000/repositories/connect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"repo_url":"https://github.com/org/repo"}'
```

Sync and query metrics:

```bash
curl -X POST http://localhost:8000/repositories/1/sync \
  -H "Authorization: Bearer <token>"

curl -X GET "http://localhost:8000/metrics/repository/1?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer <token>"
```

## Future Improvements

- Webhook-based GitHub ingestion to reduce polling
- Fine-grained permissions for project members
- Real deployment ingestion from CI/CD providers
- Async task queue (Celery/RQ) for large repos
- Grafana-compatible metrics export
