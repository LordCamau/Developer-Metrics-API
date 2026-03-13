from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.core.database import get_db
from src.schemas.repository import RepositoryConnect, RepositoryResponse
from src.services.project_service import ProjectService
from src.services.repository_service import RepositoryService


router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/connect", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def connect_repository(
    payload: RepositoryConnect, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    project = ProjectService(db).get_project(payload.project_id, user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"Project not found\")
    service = RepositoryService(db)
    try:
        repo = service.connect_repository(payload.project_id, str(payload.repo_url))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return repo


@router.get("", response_model=list[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = RepositoryService(db)
    return service.list_repositories(user.id)


@router.post("/{repo_id}/sync", response_model=RepositoryResponse)
def sync_repository(repo_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    service = RepositoryService(db)
    repo = service.repositories.get_by_id(repo_id, user.id)
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    repo = service.sync_repository(repo)
    return repo
