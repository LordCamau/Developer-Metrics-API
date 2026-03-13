"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_projects_name", "projects", ["name"], unique=False)
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"], unique=False)

    op.create_table(
        "developers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_developers_username", "developers", ["username"], unique=True)

    op.create_table(
        "repositories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("repo_url", sa.String(length=500), nullable=False),
        sa.Column("owner", sa.String(length=200), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("default_branch", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_repositories_repo_url", "repositories", ["repo_url"], unique=True)
    op.create_index("ix_repositories_owner", "repositories", ["owner"], unique=False)
    op.create_index("ix_repositories_name", "repositories", ["name"], unique=False)
    op.create_index("ix_repositories_project_id", "repositories", ["project_id"], unique=False)

    op.create_table(
        "repository_developers",
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), primary_key=True),
        sa.Column("developer_id", sa.Integer(), sa.ForeignKey("developers.id"), primary_key=True),
    )

    op.create_table(
        "commits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("developer_id", sa.Integer(), sa.ForeignKey("developers.id"), nullable=True),
        sa.Column("sha", sa.String(length=80), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=True),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_commits_sha", "commits", ["sha"], unique=True)
    op.create_index("ix_commits_repository_id", "commits", ["repository_id"], unique=False)
    op.create_index("ix_commits_developer_id", "commits", ["developer_id"], unique=False)
    op.create_index("ix_commits_committed_at", "commits", ["committed_at"], unique=False)

    op.create_table(
        "pull_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("developer_id", sa.Integer(), sa.ForeignKey("developers.id"), nullable=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"], unique=False)
    op.create_index("ix_pull_requests_developer_id", "pull_requests", ["developer_id"], unique=False)
    op.create_index("ix_pull_requests_number", "pull_requests", ["number"], unique=False)
    op.create_index("ix_pull_requests_state", "pull_requests", ["state"], unique=False)
    op.create_index("ix_pull_requests_opened_at", "pull_requests", ["opened_at"], unique=False)

    op.create_table(
        "deployments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("environment", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_deployments_repository_id", "deployments", ["repository_id"], unique=False)
    op.create_index("ix_deployments_deployed_at", "deployments", ["deployed_at"], unique=False)

    op.create_table(
        "metrics_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=True),
        sa.Column("developer_id", sa.Integer(), sa.ForeignKey("developers.id"), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_metrics_snapshots_project_id", "metrics_snapshots", ["project_id"], unique=False)
    op.create_index(
        "ix_metrics_snapshots_repository_id", "metrics_snapshots", ["repository_id"], unique=False
    )
    op.create_index(
        "ix_metrics_snapshots_developer_id", "metrics_snapshots", ["developer_id"], unique=False
    )
    op.create_index("ix_metrics_snapshots_start_date", "metrics_snapshots", ["start_date"], unique=False)
    op.create_index("ix_metrics_snapshots_end_date", "metrics_snapshots", ["end_date"], unique=False)

    op.create_table(
        "code_frequency_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("repository_id", sa.Integer(), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_code_frequency_stats_repository_id",
        "code_frequency_stats",
        ["repository_id"],
        unique=False,
    )
    op.create_index(
        "ix_code_frequency_stats_week_start",
        "code_frequency_stats",
        ["week_start"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_code_frequency_stats_week_start", table_name="code_frequency_stats")
    op.drop_index("ix_code_frequency_stats_repository_id", table_name="code_frequency_stats")
    op.drop_table("code_frequency_stats")

    op.drop_index("ix_metrics_snapshots_end_date", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_start_date", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_developer_id", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_repository_id", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_project_id", table_name="metrics_snapshots")
    op.drop_table("metrics_snapshots")

    op.drop_index("ix_deployments_deployed_at", table_name="deployments")
    op.drop_index("ix_deployments_repository_id", table_name="deployments")
    op.drop_table("deployments")

    op.drop_index("ix_pull_requests_opened_at", table_name="pull_requests")
    op.drop_index("ix_pull_requests_state", table_name="pull_requests")
    op.drop_index("ix_pull_requests_number", table_name="pull_requests")
    op.drop_index("ix_pull_requests_developer_id", table_name="pull_requests")
    op.drop_index("ix_pull_requests_repository_id", table_name="pull_requests")
    op.drop_table("pull_requests")

    op.drop_index("ix_commits_committed_at", table_name="commits")
    op.drop_index("ix_commits_developer_id", table_name="commits")
    op.drop_index("ix_commits_repository_id", table_name="commits")
    op.drop_index("ix_commits_sha", table_name="commits")
    op.drop_table("commits")

    op.drop_table("repository_developers")

    op.drop_index("ix_repositories_project_id", table_name="repositories")
    op.drop_index("ix_repositories_name", table_name="repositories")
    op.drop_index("ix_repositories_owner", table_name="repositories")
    op.drop_index("ix_repositories_repo_url", table_name="repositories")
    op.drop_table("repositories")

    op.drop_index("ix_developers_username", table_name="developers")
    op.drop_table("developers")

    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_index("ix_projects_name", table_name="projects")
    op.drop_table("projects")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
