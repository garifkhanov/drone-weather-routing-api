from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DroneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    max_range_km: float = Field(gt=0)
    max_wind_speed_ms: float = Field(gt=0)
    max_gust_ms: float = Field(gt=0)
    max_precipitation_mm: float = Field(ge=0)
    cruise_speed_kmh: float = Field(gt=0)


class DroneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    max_range_km: float | None = Field(default=None, gt=0)
    max_wind_speed_ms: float | None = Field(default=None, gt=0)
    max_gust_ms: float | None = Field(default=None, gt=0)
    max_precipitation_mm: float | None = Field(default=None, ge=0)
    cruise_speed_kmh: float | None = Field(default=None, gt=0)


class DroneResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    max_range_km: float
    max_wind_speed_ms: float
    max_gust_ms: float
    max_precipitation_mm: float
    cruise_speed_kmh: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
