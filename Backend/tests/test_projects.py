def test_user_creates_project(client, normal_token):
    response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {normal_token}"},
        json={"name": "Project Alpha", "description": "First project"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Project Alpha"
    assert data["description"] == "First project"
    assert "id" in data
    assert "owner_id" in data


def test_user_sees_only_their_projects(client, normal_token):
    client.post(
        "/projects",
        headers={"Authorization": f"Bearer {normal_token}"},
        json={"name": "User Project", "description": "Mine"}
    )

    response = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "User Project"


def test_other_user_cannot_update_project(client, normal_token):
    owner_signup = client.post(
        "/auth/signup",
        json={"username": "owner_user", "password": "Password123!"}
    )
    owner_login = client.post(
        "/auth/login",
        json={"email": "owner_user", "password": "Password123!"}
    )
    owner_token = owner_login.json()["access_token"]

    project = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"name": "Owner Project", "description": "Secret"}
    ).json()

    response = client.put(
        f"/projects/{project['id']}",
        headers={"Authorization": f"Bearer {normal_token}"},
        json={"name": "Hacked"}
    )
    assert response.status_code == 403


def test_admin_can_update_any_project(client, admin_token):
    user_signup = client.post(
        "/auth/signup",
        json={"username": "proj_user", "password": "Password123!"}
    )
    user_login = client.post(
        "/auth/login",
        json={"email": "proj_user", "password": "Password123!"}
    )
    user_token = user_login.json()["access_token"]

    project = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "User Project", "description": "Needs update"}
    ).json()

    response = client.put(
        f"/projects/{project['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Admin Updated"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Admin Updated"


def test_delete_sets_inactive_and_hides_from_list(client, normal_token):
    project = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {normal_token}"},
        json={"name": "Temp Project", "description": "To delete"}
    ).json()

    delete_response = client.delete(
        f"/projects/{project['id']}",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == project["id"]

    list_response = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {normal_token}"}
    )
    assert list_response.status_code == 200
    assert list_response.json() == []
