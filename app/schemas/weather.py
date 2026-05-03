from datetime import datetime

from pydantic import BaseModel


class WeatherPointResponse(BaseModel):
    lat: float
    lon: float
    forecast_time: datetime
    temperature_c: float | None = None
    relative_humidity_percent: float | None = None
    wind_speed_ms: float
    wind_gust_ms: float
    precipitation_mm: float
    cloud_cover_percent: float | None = None
    weather_code: int | None = None
