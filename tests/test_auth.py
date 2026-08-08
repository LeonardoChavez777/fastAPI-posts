def test_login_success(client, test_user, user_credentials):
    response = client.post(
        "/auth/login",
        data={"username": user_credentials["email"], "password": user_credentials["password"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": "wrong-password"},
    )

    assert response.status_code == 403
