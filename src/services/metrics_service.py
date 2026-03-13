from datetime import date, datetime, time, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.commit import Commit
from src.models.deployment import Deployment
from src.models.developer import Developer
from src.models.pull_request import PullRequest
from src.models.repository import Repository


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def repository_metrics(
        self,
        repo_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        developer_username: str | None = None,
    ) -> dict:
        repo = self.db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise ValueError("Repository not found")

        developer_id = None
        if developer_username:
            developer = (
                self.db.query(Developer).filter(Developer.username == developer_username).first()
            )
            if developer:
                developer_id = developer.id

        commits_q = self.db.query(Commit).filter(Commit.repository_id == repo_id)
        prs_q = self.db.query(PullRequest).filter(PullRequest.repository_id == repo_id)
        deployments_q = self.db.query(Deployment).filter(Deployment.repository_id == repo_id)

        if developer_id:
            commits_q = commits_q.filter(Commit.developer_id == developer_id)
            prs_q = prs_q.filter(PullRequest.developer_id == developer_id)

        commits_q = self._apply_date_filter(commits_q, Commit.committed_at, start_date, end_date)
        prs_q = self._apply_date_filter(prs_q, PullRequest.opened_at, start_date, end_date)
        deployments_q = self._apply_date_filter(
            deployments_q, Deployment.deployed_at, start_date, end_date
        )

        commit_count = commits_q.count()
        pr_count = prs_q.count()
        deployment_count = deployments_q.count()

        additions = commits_q.with_entities(func.coalesce(func.sum(Commit.additions), 0)).scalar()
        deletions = commits_q.with_entities(func.coalesce(func.sum(Commit.deletions), 0)).scalar()
        code_churn = (additions or 0) + (deletions or 0)

        lead_time_seconds = (
            prs_q.filter(PullRequest.merged_at.isnot(None))
            .with_entities(
                func.coalesce(func.avg(func.extract("epoch", PullRequest.merged_at - PullRequest.opened_at)), 0)
            )
            .scalar()
        )
        lead_time_hours = (lead_time_seconds or 0) / 3600

        velocity = self._compute_velocity(commit_count, start_date, end_date)
        deployment_frequency = self._compute_velocity(deployment_count, start_date, end_date)

        activity_score = (commit_count * 1.0) + (pr_count * 2.0) + (deployment_count * 3.0)

        return {
            "repository_id": repo_id,
            "commit_count": commit_count,
            "commit_velocity": velocity,
            "pull_request_count": pr_count,
            "deployment_count": deployment_count,
            "deployment_frequency": deployment_frequency,
            "code_churn": code_churn,
            "lead_time_hours": lead_time_hours,
            "developer_activity_score": activity_score,
        }

    def developer_metrics(
        self,
        username: str,
        start_date: date | None = None,
        end_date: date | None = None,
        repository_id: int | None = None,
    ) -> dict:
        developer = self.db.query(Developer).filter(Developer.username == username).first()
        if not developer:
            raise ValueError("Developer not found")

        commits_q = self.db.query(Commit).filter(Commit.developer_id == developer.id)
        prs_q = self.db.query(PullRequest).filter(PullRequest.developer_id == developer.id)
        if repository_id:
            commits_q = commits_q.filter(Commit.repository_id == repository_id)
            prs_q = prs_q.filter(PullRequest.repository_id == repository_id)

        commits_q = self._apply_date_filter(commits_q, Commit.committed_at, start_date, end_date)
        prs_q = self._apply_date_filter(prs_q, PullRequest.opened_at, start_date, end_date)

        commit_count = commits_q.count()
        pr_count = prs_q.count()
        activity_score = (commit_count * 1.0) + (pr_count * 2.0)

        return {
            "developer": username,
            "commit_count": commit_count,
            "pull_request_count": pr_count,
            "developer_activity_score": activity_score,
        }

    def project_metrics(
        self,
        project_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        repository_id: int | None = None,
    ) -> dict:
        repos_query = self.db.query(Repository).filter(Repository.project_id == project_id)
        if repository_id:
            repos_query = repos_query.filter(Repository.id == repository_id)
        repos = repos_query.all()
        if not repos:
            raise ValueError("Project not found or has no repositories")

        aggregated = {
            "commit_count": 0,
            "pull_request_count": 0,
            "deployment_count": 0,
            "code_churn": 0,
        }
        for repo in repos:
            metrics = self.repository_metrics(repo.id, start_date=start_date, end_date=end_date)
            aggregated["commit_count"] += metrics["commit_count"]
            aggregated["pull_request_count"] += metrics["pull_request_count"]
            aggregated["deployment_count"] += metrics.get("deployment_count", 0)
            aggregated["code_churn"] += metrics["code_churn"]

        aggregated["commit_velocity"] = self._compute_velocity(
            aggregated["commit_count"], start_date, end_date
        )
        aggregated["deployment_frequency"] = self._compute_velocity(
            aggregated["deployment_count"], start_date, end_date
        )
        aggregated["developer_activity_score"] = (
            aggregated["commit_count"] * 1.0 + aggregated["pull_request_count"] * 2.0
        )
        return {"project_id": project_id, **aggregated}

    def organization_metrics(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        repository_id: int | None = None,
        developer_username: str | None = None,
    ):
        repos_query = self.db.query(Repository)
        if repository_id:
            repos_query = repos_query.filter(Repository.id == repository_id)
        repos = repos_query.all()
        if not repos:
            return {"commit_count": 0, "pull_request_count": 0, "deployment_count": 0}

        commit_count = 0
        pr_count = 0
        deployment_count = 0
        code_churn = 0

        for repo in repos:
            metrics = self.repository_metrics(
                repo.id,
                start_date=start_date,
                end_date=end_date,
                developer_username=developer_username,
            )
            commit_count += metrics["commit_count"]
            pr_count += metrics["pull_request_count"]
            deployment_count += metrics.get("deployment_count", 0)
            code_churn += metrics["code_churn"]

        return {
            "commit_count": commit_count,
            "pull_request_count": pr_count,
            "deployment_count": deployment_count,
            "code_churn": code_churn,
        }

    @staticmethod
    def _apply_date_filter(query, column, start_date, end_date):
        if start_date:
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            query = query.filter(column >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            query = query.filter(column <= end_dt)
        return query

    @staticmethod
    def _compute_velocity(count: int, start_date: date | None, end_date: date | None) -> float:
        if start_date and end_date and end_date >= start_date:
            days = (end_date - start_date).days + 1
            return round(count / max(days, 1), 2)
        return float(count)
