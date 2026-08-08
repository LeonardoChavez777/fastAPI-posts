def _create_post(client, auth_headers):
    return client.post(
        "/posts/",
        json={"title": "Votable post", "content": "content", "published": True},
        headers=auth_headers,
    ).json()


def test_vote_on_post(client, auth_headers):
    post = _create_post(client, auth_headers)

    response = client.post("/vote/", json={"post_id": post["Id"], "dir": 1}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["message"] == "has dado laiki"


def test_vote_count_in_posts(client, auth_headers):
    post = _create_post(client, auth_headers)
    client.post("/vote/", json={"post_id": post["Id"], "dir": 1}, headers=auth_headers)

    response = client.get("/posts/")

    assert response.status_code == 200
    assert response.json()[0]["votos"] == 1


def test_remove_vote(client, auth_headers):
    post = _create_post(client, auth_headers)
    client.post("/vote/", json={"post_id": post["Id"], "dir": 1}, headers=auth_headers)

    response = client.post("/vote/", json={"post_id": post["Id"], "dir": 0}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["message"] == "has quitado el laiki"


def test_duplicate_vote_conflict(client, auth_headers):
    post = _create_post(client, auth_headers)
    client.post("/vote/", json={"post_id": post["Id"], "dir": 1}, headers=auth_headers)

    response = client.post("/vote/", json={"post_id": post["Id"], "dir": 1}, headers=auth_headers)

    assert response.status_code == 409
