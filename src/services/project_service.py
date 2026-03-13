from sqlalchemy.orm import Session

from src.models.project import Project
from src.repositories.project_repo import ProjectRepository


class ProjectService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)

    def create_project(self, owner_id: int, name: str, description: str | None) -> Project:
        return self.projects.create(owner_id=owner_id, name=name, description=description)

    def list_projects(self, owner_id: int) -> list[Project]:
        return self.projects.list_by_owner(owner_id)

    def get_project(self, project_id: int, owner_id: int) -> Project | None:
        return self.projects.get_by_id(project_id, owner_id)

    def delete_project(self, project: Project) -> None:
        self.projects.delete(project)
