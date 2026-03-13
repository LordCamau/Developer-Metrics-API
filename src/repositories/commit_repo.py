from sqlalchemy.orm import Session

from src.models.commit import Commit


class CommitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_sha(self, sha: str) -> Commit | None:
        return self.db.query(Commit).filter(Commit.sha == sha).first()

    def add(self, commit: Commit) -> Commit:
        self.db.add(commit)
        self.db.commit()
        self.db.refresh(commit)
        return commit
