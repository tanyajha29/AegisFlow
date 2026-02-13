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


def test_admin_can_list_users(client, admin_token):
    response = client.get(
        "/auth/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_normal_user_forbidden_admin_routes(client, normal_token):
    response = client.get(
        "/auth/admin/users",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert response.status_code == 403


def test_admin_can_change_role(client, admin_token, normal_user):
    response = client.patch(
        f"/auth/admin/users/{normal_user['id']}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role_name": "admin"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == normal_user["id"]


def test_deactivated_user_cannot_login(client, admin_token, normal_user):
    response = client.patch(
        f"/auth/admin/users/{normal_user['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 200

    login = client.post(
        "/auth/login",
        json={"email": normal_user["username"], "password": "Password123!"}
    )
    assert login.status_code == 403
