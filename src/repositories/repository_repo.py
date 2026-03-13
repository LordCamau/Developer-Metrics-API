from sqlalchemy.orm import Session

from src.models.repository import Repository


class RepositoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        project_id: int,
        repo_url: str,
        owner: str,
        name: str,
        default_branch: str | None,
    ) -> Repository:
        repo = Repository(
            project_id=project_id,
            repo_url=repo_url,
            owner=owner,
            name=name,
            default_branch=default_branch,
        )
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def list_by_owner(self, owner_id: int) -> list[Repository]:
        return (
            self.db.query(Repository)
            .join(Repository.project)
            .filter(Repository.project.has(owner_id=owner_id))
            .all()
        )

    def get_by_id(self, repo_id: int, owner_id: int) -> Repository | None:
        return (
            self.db.query(Repository)
            .join(Repository.project)
            .filter(Repository.id == repo_id, Repository.project.has(owner_id=owner_id))
            .first()
        )

    def list_all(self) -> list[Repository]:
        return self.db.query(Repository).all()
