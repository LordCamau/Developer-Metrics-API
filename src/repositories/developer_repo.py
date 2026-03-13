from sqlalchemy.orm import Session

from src.models.developer import Developer


class DeveloperRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Developer | None:
        return self.db.query(Developer).filter(Developer.username == username).first()

    def create(self, username: str, email: str | None, avatar_url: str | None) -> Developer:
        developer = Developer(username=username, email=email, avatar_url=avatar_url)
        self.db.add(developer)
        self.db.commit()
        self.db.refresh(developer)
        return developer
