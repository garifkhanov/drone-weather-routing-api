from app.api.deps import get_weather_client
from tests.conftest import (
    FakeWeatherClient,
    auth_headers,
    create_drone,
    create_user_token,
    route_payload,
)


def test_plan_route_success(client):
    token = create_user_token(client)
    drone = create_drone(client, token, max_range_km=200)

    response = client.post(
        "/routes/plan",
        json=route_payload(drone["id"], grid_size=5),
        headers=auth_headers(token),
    )
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["status"] == "route_found"
    assert response_json["route_result_id"]
    assert len(response_json["route"]) > 0

    result_response = client.get(
        f"/routes/results/{response_json['route_result_id']}",
        headers=auth_headers(token),
    )
    waypoints_response = client.get(
        f"/routes/results/{response_json['route_result_id']}/waypoints",
        headers=auth_headers(token),
    )

    assert result_response.status_code == 200
    assert result_response.json()["status"] == "route_found"
    assert waypoints_response.status_code == 200
    assert len(waypoints_response.json()) == len(response_json["route"])


def test_plan_route_blocked_by_weather(client):
    token = create_user_token(client)
    drone = create_drone(client, token, max_range_km=200)
    client.app.dependency_overrides[get_weather_client] = lambda: FakeWeatherClient(
        wind_speed_ms=99,
        wind_gust_ms=99,
        precipitation_mm=9,
    )

    response = client.post(
        "/routes/plan",
        json=route_payload(drone["id"], grid_size=5),
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "route_not_found"
    assert response.json()["reason"]


def test_plan_route_exceeds_range(client):
    token = create_user_token(client)
    drone = create_drone(client, token, max_range_km=1)

    response = client.post(
        "/routes/plan",
        json=route_payload(drone["id"], grid_size=5),
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "route_not_found"
    assert response.json()["reason"] == "Route exceeds drone maximum range."


def test_user_cannot_plan_route_with_another_users_drone(client):
    first_token = create_user_token(client)
    second_token = create_user_token(client)
    second_drone = create_drone(client, second_token)

    response = client.post(
        "/routes/plan",
        json=route_payload(second_drone["id"], grid_size=5),
        headers=auth_headers(first_token),
    )

    assert response.status_code == 404
