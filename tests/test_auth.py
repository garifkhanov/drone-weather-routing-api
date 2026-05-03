from tests.conftest import login_user, register_user


def test_register_user_success(client, unique_email):
    response, _, _ = register_user(client, unique_email)

    assert response.status_code == 201
    assert response.json()["email"] == unique_email
    assert "hashed_password" not in response.json()


def test_register_duplicate_email_fails(client, unique_email):
    register_user(client, unique_email)

    response, _, _ = register_user(client, unique_email)

    assert response.status_code == 409


def test_login_success(client, unique_email):
    _, _, password = register_user(client, unique_email)

    token = login_user(client, unique_email, password)

    assert token


def test_login_wrong_password_fails(client, unique_email):
    register_user(client, unique_email)

    response = client.post(
        "/auth/login",
        json={"email": unique_email, "password": "wrong-password"},
    )

    assert response.status_code == 401
