def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={"username": "alice", "password": "Password123!"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["is_active"] is True
    assert "id" in data


def test_login(client):
    client.post(
        "/auth/signup",
        json={"username": "bob", "password": "Password123!"}
    )

    response = client.post(
        "/auth/login",
        json={"email": "bob", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_route(client):
    client.post(
        "/auth/signup",
        json={"username": "carol", "password": "Password123!"}
    )

    login = client.post(
        "/auth/login",
        json={"email": "carol", "password": "Password123!"}
    )
    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "carol"
