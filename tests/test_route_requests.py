from tests.conftest import (
    auth_headers,
    create_drone,
    create_user_token,
    route_payload,
)


def test_create_route_request(client):
    token = create_user_token(client)
    drone = create_drone(client, token)

    response = client.post(
        "/route-requests",
        json=route_payload(drone["id"]),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["drone_id"] == drone["id"]


def test_list_route_requests(client):
    token = create_user_token(client)
    drone = create_drone(client, token)
    client.post(
        "/route-requests",
        json=route_payload(drone["id"]),
        headers=auth_headers(token),
    )

    response = client.get("/route-requests", headers=auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_user_cannot_create_route_request_with_another_users_drone(client):
    first_token = create_user_token(client)
    second_token = create_user_token(client)
    second_drone = create_drone(client, second_token)

    response = client.post(
        "/route-requests",
        json=route_payload(second_drone["id"]),
        headers=auth_headers(first_token),
    )

    assert response.status_code == 404
