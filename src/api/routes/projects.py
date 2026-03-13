from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.database import get_db
from src.schemas.project import ProjectCreate, ProjectResponse
from src.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    service = ProjectService(db)
    project = service.create_project(user.id, payload.name, payload.description)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ProjectService(db)
    return service.list_projects(user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ProjectService(db)
    project = service.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = ProjectService(db)
    project = service.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    service.delete_project(project)
    return None
