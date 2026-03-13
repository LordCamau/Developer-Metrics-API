from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool

    model_config = {"from_attributes": True}
