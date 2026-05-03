from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db, get_weather_client
from app.db.base import Base
from app.main import app
from app.services.weather_client import Coordinate, WeatherData, WeatherClientError


class FakeWeatherClient:
    def __init__(
        self,
        wind_speed_ms: float = 4.0,
        wind_gust_ms: float = 6.0,
        precipitation_mm: float = 0.0,
    ) -> None:
        self.wind_speed_ms = wind_speed_ms
        self.wind_gust_ms = wind_gust_ms
        self.precipitation_mm = precipitation_mm

    def get_hourly_weather_for_points(
        self,
        points: list[Coordinate],
        forecast_time: datetime,
    ) -> list[WeatherData]:
        normalized_time = forecast_time
        if normalized_time.tzinfo is None:
            normalized_time = normalized_time.replace(tzinfo=timezone.utc)

        return [
            WeatherData(
                coordinate=point,
                forecast_time=normalized_time,
                wind_speed_ms=self.wind_speed_ms,
                wind_gust_ms=self.wind_gust_ms,
                precipitation_mm=self.precipitation_mm,
                weather_code=1,
            )
            for point in points
        ]


class FailingWeatherClient:
    def get_hourly_weather_for_points(
        self,
        points: list[Coordinate],
        forecast_time: datetime,
    ) -> list[WeatherData]:
        raise WeatherClientError("Weather API unavailable")


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_weather_client] = lambda: FakeWeatherClient()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="unique_email")
def unique_email_fixture() -> str:
    return f"user-{uuid4().hex[:10]}@example.com"


def register_user(
    client: TestClient,
    email: str | None = None,
    password: str = "secret123",
):
    email = email or f"user-{uuid4().hex[:10]}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    return response, email, password


def login_user(client: TestClient, email: str, password: str = "secret123") -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_user_token(client: TestClient) -> str:
    _, email, password = register_user(client)
    return login_user(client, email, password)


def create_drone(
    client: TestClient,
    token: str,
    max_range_km: float = 100,
) -> dict:
    response = client.post(
        "/drones",
        json={
            "name": "Test Drone",
            "max_range_km": max_range_km,
            "max_wind_speed_ms": 10,
            "max_gust_ms": 15,
            "max_precipitation_mm": 0.5,
            "cruise_speed_kmh": 50,
        },
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def route_payload(drone_id: int, grid_size: int = 8) -> dict:
    return {
        "drone_id": drone_id,
        "start_lat": 59.3293,
        "start_lon": 18.0686,
        "end_lat": 59.8586,
        "end_lon": 17.6389,
        "departure_time": "2026-05-03T10:00:00",
        "grid_size": grid_size,
        "corridor_width_km": 25,
    }
