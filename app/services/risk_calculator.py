from typing import Protocol

from app.services.weather_client import WeatherData


class WeatherLimits(Protocol):
    max_wind_speed_ms: float
    max_gust_ms: float
    max_precipitation_mm: float


def calculate_weather_risk(
    weather_data: WeatherData,
    drone: WeatherLimits,
) -> float:
    wind_ratio = weather_data.wind_speed_ms / drone.max_wind_speed_ms
    gust_ratio = weather_data.wind_gust_ms / drone.max_gust_ms
    precipitation_ratio = (
        weather_data.precipitation_mm
        / max(drone.max_precipitation_mm, 0.1)
    )

    risk = (
        0.5 * wind_ratio
        + 0.3 * gust_ratio
        + 0.2 * precipitation_ratio
    )

    return min(max(risk, 0.0), 1.0)


def is_weather_blocked(
    weather_data: WeatherData,
    drone: WeatherLimits,
) -> bool:
    return (
        weather_data.wind_speed_ms > drone.max_wind_speed_ms
        or weather_data.wind_gust_ms > drone.max_gust_ms
        or weather_data.precipitation_mm > drone.max_precipitation_mm
    )
