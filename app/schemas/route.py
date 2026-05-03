import json
from datetime import datetime
from json import JSONDecodeError
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class RouteRequestCreate(BaseModel):
    drone_id: int = Field(gt=0)
    start_lat: Latitude
    start_lon: Longitude
    end_lat: Latitude
    end_lon: Longitude
    departure_time: datetime
    grid_size: int = Field(default=12, ge=5, le=30)
    corridor_width_km: float = Field(default=25, ge=1, le=100)


class RouteRequestResponse(BaseModel):
    id: int
    user_id: int
    drone_id: int
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    departure_time: datetime
    grid_size: int
    corridor_width_km: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoutePlanRequest(RouteRequestCreate):
    pass


class WeatherSummary(BaseModel):
    max_wind_speed_ms: float
    max_gust_ms: float
    max_precipitation_mm: float


class RouteWaypointResponse(BaseModel):
    lat: float
    lon: float
    weather_risk: float = Field(ge=0, le=1)

    model_config = ConfigDict(from_attributes=True)


class RoutePlanResponse(BaseModel):
    status: str
    route_request_id: int
    route_result_id: int
    total_distance_km: float | None = None
    effective_distance_km: float | None = None
    risk_score: float | None = Field(default=None, ge=0, le=1)
    weather_summary: WeatherSummary | None = None
    route: list[RouteWaypointResponse] = Field(default_factory=list)
    reason: str | None = None
    explanation: list[str] = Field(default_factory=list)


class RouteResultResponse(BaseModel):
    id: int
    route_request_id: int
    status: str
    total_distance_km: float | None = None
    effective_distance_km: float | None = None
    risk_score: float | None = Field(default=None, ge=0, le=1)
    reason: str | None = None
    explanation: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("explanation", mode="before")
    @classmethod
    def parse_explanation(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except JSONDecodeError:
                return [value]
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            return [str(parsed)]
        return [str(value)]
