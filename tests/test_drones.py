from tests.conftest import auth_headers, create_drone, create_user_token


def test_create_drone_authorized(client):
    token = create_user_token(client)

    drone = create_drone(client, token)

    assert drone["name"] == "Test Drone"
    assert drone["max_range_km"] == 100


def test_create_drone_unauthorized_fails(client):
    response = client.post(
        "/drones",
        json={
            "name": "No Token Drone",
            "max_range_km": 100,
            "max_wind_speed_ms": 10,
            "max_gust_ms": 15,
            "max_precipitation_mm": 0.5,
            "cruise_speed_kmh": 50,
        },
    )

    assert response.status_code == 401


def test_list_only_own_drones(client):
    first_token = create_user_token(client)
    second_token = create_user_token(client)
    create_drone(client, first_token)
    create_drone(client, second_token)

    first_response = client.get("/drones", headers=auth_headers(first_token))
    second_response = client.get("/drones", headers=auth_headers(second_token))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(first_response.json()) == 1
    assert len(second_response.json()) == 1
    assert first_response.json()[0]["owner_id"] != second_response.json()[0]["owner_id"]


def test_update_drone(client):
    token = create_user_token(client)
    drone = create_drone(client, token)

    response = client.patch(
        f"/drones/{drone['id']}",
        json={"name": "Updated Drone", "max_range_km": 120},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Drone"
    assert response.json()["max_range_km"] == 120


def test_delete_drone(client):
    token = create_user_token(client)
    drone = create_drone(client, token)

    delete_response = client.delete(
        f"/drones/{drone['id']}",
        headers=auth_headers(token),
    )
    get_response = client.get(
        f"/drones/{drone['id']}",
        headers=auth_headers(token),
    )

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
