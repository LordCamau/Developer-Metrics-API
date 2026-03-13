from jose import JWTError
from sqlalchemy.orm import Session

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.models.user import User
from src.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, email: str, username: str, password: str) -> User:
        if self.users.get_by_email(email) or self.users.get_by_username(username):
            raise ValueError("User already exists")
        hashed = hash_password(password)
        return self.users.create(email=email, username=username, hashed_password=hashed)

    def login(self, username: str, password: str) -> dict:
        user = self.users.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
        }

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            raise ValueError("Invalid token") from exc

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        subject = payload.get("sub")
        if not subject:
            raise ValueError("Invalid token subject")

        return {"access_token": create_access_token(subject)}
