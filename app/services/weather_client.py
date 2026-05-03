from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

import httpx


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float


@dataclass(frozen=True)
class WeatherData:
    coordinate: Coordinate
    forecast_time: datetime
    wind_speed_ms: float
    wind_gust_ms: float
    precipitation_mm: float
    weather_code: int | None


class WeatherClientError(RuntimeError):
    pass


class WeatherClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def get_hourly_weather_for_points(
        self,
        points: Sequence[Coordinate],
        forecast_time: datetime,
    ) -> list[WeatherData]:
        return [
            self._get_hourly_weather_for_point(point, forecast_time)
            for point in points
        ]

    def _get_hourly_weather_for_point(
        self,
        point: Coordinate,
        forecast_time: datetime,
    ) -> WeatherData:
        params = {
            "latitude": point.lat,
            "longitude": point.lon,
            "hourly": (
                "wind_speed_10m,wind_gusts_10m,"
                "precipitation,weather_code"
            ),
            "wind_speed_unit": "ms",
            "timezone": "UTC",
            "start_date": forecast_time.date().isoformat(),
            "end_date": forecast_time.date().isoformat(),
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                payload = response.json()
            return self._parse_weather_response(point, payload, forecast_time)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise WeatherClientError("Open-Meteo weather request failed") from exc

    def _parse_weather_response(
        self,
        point: Coordinate,
        payload: dict[str, Any],
        forecast_time: datetime,
    ) -> WeatherData:
        hourly = payload["hourly"]
        times = hourly["time"]
        nearest_index = self._find_nearest_hour_index(times, forecast_time)
        weather_code = hourly["weather_code"][nearest_index]

        return WeatherData(
            coordinate=point,
            forecast_time=self._parse_open_meteo_time(times[nearest_index]),
            wind_speed_ms=float(hourly["wind_speed_10m"][nearest_index]),
            wind_gust_ms=float(hourly["wind_gusts_10m"][nearest_index]),
            precipitation_mm=float(hourly["precipitation"][nearest_index]),
            weather_code=None if weather_code is None else int(weather_code),
        )

    def _find_nearest_hour_index(
        self,
        times: Sequence[str],
        forecast_time: datetime,
    ) -> int:
        if not times:
            raise WeatherClientError("Open-Meteo response has no hourly data")

        target_time = self._normalize_datetime(forecast_time)
        parsed_times = [self._parse_open_meteo_time(time_value) for time_value in times]

        return min(
            range(len(parsed_times)),
            key=lambda index: abs(
                (parsed_times[index] - target_time).total_seconds(),
            ),
        )

    @staticmethod
    def _parse_open_meteo_time(value: str) -> datetime:
        parsed_time = datetime.fromisoformat(value)
        return WeatherClient._normalize_datetime(parsed_time)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
