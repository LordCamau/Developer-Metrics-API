

def _auth_header(client):
    register = client.post(
        "/auth/register",
        json={"email": "metrics@example.com", "username": "metrics", "password": "password123"},
    )
    tokens = register.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_metrics_after_sync(client, mocker):
    headers = _auth_header(client)
    project = client.post("/projects", json={"name": "Team B"}, headers=headers)
    project_id = project.json()["id"]
    repo = client.post(
        "/repositories/connect",
        json={"project_id": project_id, "repo_url": "https://github.com/org/repo"},
        headers=headers,
    )
    repo_id = repo.json()["id"]

    mocker.patch(
        "src.services.github_service.GitHubService.fetch_contributors",
        return_value=[{"login": "octo", "avatar_url": "https://example.com"}],
    )
    mocker.patch(
        "src.services.github_service.GitHubService.fetch_commits",
        return_value=[
            {
                "sha": "abc",
                "commit": {"message": "init", "author": {"date": "2024-01-01T00:00:00Z"}},
                "author": {"login": "octo", "avatar_url": "https://example.com"},
                "stats": {"additions": 10, "deletions": 2},
            }
        ],
    )
    mocker.patch(
        "src.services.github_service.GitHubService.fetch_pull_requests",
        return_value=[
            {
                "number": 2,
                "title": "Fix bug",
                "state": "closed",
                "created_at": "2024-01-02T00:00:00Z",
                "merged_at": "2024-01-03T00:00:00Z",
                "closed_at": "2024-01-03T00:00:00Z",
                "user": {"login": "octo", "avatar_url": "https://example.com"},
            }
        ],
    )
    mocker.patch(
        "src.services.github_service.GitHubService.fetch_code_frequency",
        return_value=[[1700000000, 5, -3]],
    )

    client.post(f"/repositories/{repo_id}/sync", headers=headers)

    metrics = client.get(f"/metrics/repository/{repo_id}", headers=headers)
    assert metrics.status_code == 200
    data = metrics.json()["metrics"]
    assert data["commit_count"] == 1
    assert data["pull_request_count"] == 1
    assert data["code_churn"] == 12
