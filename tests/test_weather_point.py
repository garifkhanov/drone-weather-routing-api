from app.api.deps import get_weather_client
from tests.conftest import FailingWeatherClient, auth_headers, create_user_token


def test_authorized_user_can_request_weather_point(client):
    token = create_user_token(client)

    response = client.get(
        "/weather/point",
        params={
            "lat": 59.3293,
            "lon": 18.0686,
            "forecast_time": "2026-05-03T10:00:00",
        },
        headers=auth_headers(token),
    )
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["lat"] == 59.3293
    assert response_json["lon"] == 18.0686
    assert response_json["temperature_c"] == 12.4
    assert response_json["relative_humidity_percent"] == 75
    assert response_json["wind_speed_ms"] == 4.0
    assert response_json["cloud_cover_percent"] == 64


def test_unauthorized_weather_point_request_fails(client):
    response = client.get(
        "/weather/point",
        params={"lat": 59.3293, "lon": 18.0686},
    )

    assert response.status_code == 401


def test_weather_point_returns_502_when_weather_client_fails(client):
    token = create_user_token(client)
    client.app.dependency_overrides[get_weather_client] = lambda: FailingWeatherClient()

    response = client.get(
        "/weather/point",
        params={"lat": 59.3293, "lon": 18.0686},
        headers=auth_headers(token),
    )

    assert response.status_code == 502
