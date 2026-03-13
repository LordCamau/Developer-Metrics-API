from sqlalchemy.orm import Session

from src.models.pull_request import PullRequest


class PullRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_number(self, repository_id: int, number: int) -> PullRequest | None:
        return (
            self.db.query(PullRequest)
            .filter(PullRequest.repository_id == repository_id, PullRequest.number == number)
            .first()
        )

    def add(self, pr: PullRequest) -> PullRequest:
        self.db.add(pr)
        self.db.commit()
        self.db.refresh(pr)
        return pr
