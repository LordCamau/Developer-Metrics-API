

def test_auth_flow(client):
    register = client.post(
        "/auth/register",
        json={"email": "dev@example.com", "username": "dev1", "password": "password123"},
    )
    assert register.status_code == 200
    tokens = register.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    login = client.post(
        "/auth/login", json={"username": "dev1", "password": "password123"}
    )
    assert login.status_code == 200

    refresh = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]
