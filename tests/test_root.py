def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "actualizado automaticamente gracias a github actions y docker compose"}
