

def _auth_header(client):
    register = client.post(
        "/auth/register",
        json={"email": "query@example.com", "username": "queryuser", "password": "password123"},
    )
    tokens = register.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_metrics_queries(client, mocker):
    headers = _auth_header(client)
    project = client.post("/projects", json={"name": "Team C"}, headers=headers)
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
                "sha": "def",
                "commit": {"message": "feat", "author": {"date": "2024-01-01T00:00:00Z"}},
                "author": {"login": "octo", "avatar_url": "https://example.com"},
                "stats": {"additions": 4, "deletions": 1},
            }
        ],
    )
    mocker.patch(
        "src.services.github_service.GitHubService.fetch_pull_requests",
        return_value=[
            {
                "number": 3,
                "title": "PR",
                "state": "open",
                "created_at": "2024-01-02T00:00:00Z",
                "merged_at": None,
                "closed_at": None,
                "user": {"login": "octo", "avatar_url": "https://example.com"},
            }
        ],
    )
    mocker.patch(
        "src.services.github_service.GitHubService.fetch_code_frequency",
        return_value=[[1700000000, 1, -1]],
    )

    client.post(f"/repositories/{repo_id}/sync", headers=headers)

    dev_metrics = client.get("/metrics/developer/octo", headers=headers)
    assert dev_metrics.status_code == 200
    assert dev_metrics.json()["metrics"]["commit_count"] == 1

    project_metrics = client.get(f"/metrics/project/{project_id}", headers=headers)
    assert project_metrics.status_code == 200
    assert project_metrics.json()["metrics"]["commit_count"] == 1
