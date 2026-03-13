from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.commit import Commit
from src.models.code_frequency import CodeFrequencyStat
from src.models.pull_request import PullRequest
from src.repositories.commit_repo import CommitRepository
from src.repositories.developer_repo import DeveloperRepository
from src.repositories.pull_request_repo import PullRequestRepository
from src.repositories.repository_repo import RepositoryRepository
from src.services.github_service import GitHubService
from src.utils.github import parse_repo_url


class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repositories = RepositoryRepository(db)
        self.developers = DeveloperRepository(db)
        self.commits = CommitRepository(db)
        self.pull_requests = PullRequestRepository(db)
        self.github = GitHubService()

    def connect_repository(self, project_id: int, repo_url: str):
        owner, name = parse_repo_url(repo_url)
        return self.repositories.create(
            project_id=project_id,
            repo_url=repo_url,
            owner=owner,
            name=name,
            default_branch=None,
        )

    def list_repositories(self, owner_id: int):
        return self.repositories.list_by_owner(owner_id)

    def sync_repository(self, repository):
        owner = repository.owner
        name = repository.name

        contributors = self.github.fetch_contributors(owner, name)
        for contributor in contributors:
            login = contributor.get("login")
            if not login:
                continue
            developer = self.developers.get_by_username(login)
            if not developer:
                developer = self.developers.create(
                    username=login,
                    email=None,
                    avatar_url=contributor.get("avatar_url"),
                )
            if developer not in repository.developers:
                repository.developers.append(developer)

        commits = self.github.fetch_commits(owner, name)
        for item in commits:
            sha = item.get("sha")
            if not sha or self.commits.get_by_sha(sha):
                continue
            commit_info = item.get("commit", {})
            author_info = item.get("author") or {}
            commit_author = commit_info.get("author", {})
            committed_at = commit_author.get("date")
            if not committed_at:
                continue
            developer = None
            if author_info.get("login"):
                developer = self.developers.get_by_username(author_info.get("login"))
                if not developer:
                    developer = self.developers.create(
                        username=author_info.get("login"),
                        email=None,
                        avatar_url=author_info.get("avatar_url"),
                    )
            commit = Commit(
                repository_id=repository.id,
                developer_id=developer.id if developer else None,
                sha=sha,
                message=commit_info.get("message"),
                committed_at=datetime.fromisoformat(committed_at.replace("Z", "+00:00")),
                additions=item.get("stats", {}).get("additions", 0),
                deletions=item.get("stats", {}).get("deletions", 0),
            )
            self.db.add(commit)

        pull_requests = self.github.fetch_pull_requests(owner, name)
        for item in pull_requests:
            number = item.get("number")
            if number is None or self.pull_requests.get_by_number(repository.id, number):
                continue
            user_info = item.get("user") or {}
            developer = None
            if user_info.get("login"):
                developer = self.developers.get_by_username(user_info.get("login"))
                if not developer:
                    developer = self.developers.create(
                        username=user_info.get("login"),
                        email=None,
                        avatar_url=user_info.get("avatar_url"),
                    )
            pr = PullRequest(
                repository_id=repository.id,
                developer_id=developer.id if developer else None,
                number=number,
                title=item.get("title"),
                state=item.get("state", "open"),
                opened_at=self._parse_datetime(item.get("created_at")),
                merged_at=self._parse_datetime(item.get("merged_at")),
                closed_at=self._parse_datetime(item.get("closed_at")),
            )
            self.db.add(pr)

        code_frequency = self.github.fetch_code_frequency(owner, name)
        for entry in code_frequency:
            if len(entry) < 3:
                continue
            week_ts, additions, deletions = entry[0], entry[1], entry[2]
            week_start = datetime.fromtimestamp(week_ts, tz=timezone.utc).date()
            stat = CodeFrequencyStat(
                repository_id=repository.id,
                week_start=week_start,
                additions=additions,
                deletions=abs(deletions),
            )
            self.db.add(stat)

        repository.last_synced_at = datetime.now(tz=timezone.utc)
        self.db.commit()
        self.db.refresh(repository)
        return repository

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
