def _create_post(client, auth_headers, sample_post):
    return client.post("/posts/", json=sample_post, headers=auth_headers)


def test_create_post(client, auth_headers, sample_post):
    response = _create_post(client, auth_headers, sample_post)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_post["title"]
    assert data["content"] == sample_post["content"]
    assert data["owner_id"] is not None


def test_get_posts(client, auth_headers, sample_post):
    _create_post(client, auth_headers, sample_post)

    response = client.get("/posts/")

    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["Post"]["title"] == sample_post["title"]
    assert posts[0]["votos"] == 0


def test_get_post_by_id(client, auth_headers, sample_post):
    created = _create_post(client, auth_headers, sample_post).json()

    response = client.get(f"/posts/{created['Id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["Post"]["Id"] == created["Id"]


def test_get_my_posts(client, auth_headers, sample_post):
    _create_post(client, auth_headers, sample_post)

    response = client.get("/posts/myposts", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_post(client, auth_headers, sample_post):
    created = _create_post(client, auth_headers, sample_post).json()
    updated_post = {**sample_post, "title": "Updated title"}

    response = client.put(f"/posts/{created['Id']}", json=updated_post, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


def test_delete_post(client, auth_headers, sample_post):
    created = _create_post(client, auth_headers, sample_post).json()

    response = client.delete(f"/posts/{created['Id']}", headers=auth_headers)

    assert response.status_code == 204


def test_delete_post_forbidden_for_other_user(client, auth_headers, sample_post, user_credentials):
    created = _create_post(client, auth_headers, sample_post).json()

    other_user = {"email": "other@example.com", "password": "secret123"}
    client.post("/users/", json=other_user)
    other_login = client.post(
        "/auth/login",
        data={"username": other_user["email"], "password": other_user["password"]},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.delete(f"/posts/{created['Id']}", headers=other_headers)

    assert response.status_code == 403
