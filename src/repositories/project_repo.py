from sqlalchemy.orm import Session

from src.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: int, name: str, description: str | None) -> Project:
        project = Project(owner_id=owner_id, name=name, description=description)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_by_owner(self, owner_id: int) -> list[Project]:
        return self.db.query(Project).filter(Project.owner_id == owner_id).all()

    def get_by_id(self, project_id: int, owner_id: int) -> Project | None:
        return (
            self.db.query(Project)
            .filter(Project.id == project_id, Project.owner_id == owner_id)
            .first()
        )

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()
