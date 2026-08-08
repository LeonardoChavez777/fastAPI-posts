def test_create_user(client, user_credentials):
    response = client.post("/users/", json=user_credentials)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_credentials["email"]
    assert "Id" in data
    assert "password" not in data


def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user['Id']}")

    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]


def test_get_user_not_found(client):
    response = client.get("/users/9999")

    assert response.status_code == 404
