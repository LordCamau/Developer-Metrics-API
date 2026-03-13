from pydantic import BaseModel, HttpUrl


class RepositoryConnect(BaseModel):
    project_id: int
    repo_url: HttpUrl


class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    repo_url: str
    owner: str
    name: str
    default_branch: str | None = None

    model_config = {"from_attributes": True}
