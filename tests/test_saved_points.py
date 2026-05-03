from tests.conftest import auth_headers, create_user_token


def saved_point_payload(name: str = "Home") -> dict:
    return {
        "name": name,
        "lat": 59.3293,
        "lon": 18.0686,
        "description": "Main start point",
    }


def test_create_saved_point(client):
    token = create_user_token(client)

    response = client.post(
        "/saved-points",
        json=saved_point_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Home"
    assert response.json()["user_id"]


def test_list_saved_points(client):
    token = create_user_token(client)
    client.post(
        "/saved-points",
        json=saved_point_payload(),
        headers=auth_headers(token),
    )

    response = client.get("/saved-points", headers=auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_saved_point(client):
    token = create_user_token(client)
    create_response = client.post(
        "/saved-points",
        json=saved_point_payload(),
        headers=auth_headers(token),
    )

    response = client.patch(
        f"/saved-points/{create_response.json()['id']}",
        json={"name": "Airfield", "description": "Training area"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Airfield"
    assert response.json()["description"] == "Training area"


def test_delete_saved_point(client):
    token = create_user_token(client)
    create_response = client.post(
        "/saved-points",
        json=saved_point_payload(),
        headers=auth_headers(token),
    )

    delete_response = client.delete(
        f"/saved-points/{create_response.json()['id']}",
        headers=auth_headers(token),
    )
    list_response = client.get("/saved-points", headers=auth_headers(token))

    assert delete_response.status_code == 204
    assert list_response.json() == []


def test_user_cannot_access_another_users_saved_point(client):
    first_token = create_user_token(client)
    second_token = create_user_token(client)
    create_response = client.post(
        "/saved-points",
        json=saved_point_payload("Second user point"),
        headers=auth_headers(second_token),
    )

    response = client.get(
        f"/saved-points/{create_response.json()['id']}",
        headers=auth_headers(first_token),
    )

    assert response.status_code == 404
