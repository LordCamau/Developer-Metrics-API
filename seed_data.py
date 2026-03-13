from src.core.database import SessionLocal
from src.core.security import hash_password
from src.models.user import User
from src.models.project import Project
from src.models.repository import Repository


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "demo").first()
        if not user:
            user = User(
                email="demo@example.com",
                username="demo",
                hashed_password=hash_password("password123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        project = db.query(Project).filter(Project.owner_id == user.id).first()
        if not project:
            project = Project(name="Demo Project", description="Sample data", owner_id=user.id)
            db.add(project)
            db.commit()
            db.refresh(project)

        repo = db.query(Repository).filter(Repository.project_id == project.id).first()
        if not repo:
            repo = Repository(
                project_id=project.id,
                repo_url="https://github.com/org/repo",
                owner="org",
                name="repo",
                default_branch="main",
            )
            db.add(repo)
            db.commit()
        print("Seed data created")
    finally:
        db.close()


if __name__ == "__main__":
    main()
