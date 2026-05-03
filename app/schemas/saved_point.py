from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.route import Latitude, Longitude


class SavedPointCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    lat: Latitude
    lon: Longitude
    description: str | None = Field(default=None, max_length=500)


class SavedPointUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    lat: Latitude | None = None
    lon: Longitude | None = None
    description: str | None = Field(default=None, max_length=500)


class SavedPointResponse(BaseModel):
    id: int
    user_id: int
    name: str
    lat: float
    lon: float
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
