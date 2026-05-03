from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_weather_client
from app.models.user import User
from app.schemas.weather import WeatherPointResponse
from app.services.weather_client import WeatherClient, WeatherClientError


router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/point", response_model=WeatherPointResponse)
def get_weather_point(
    _current_user: Annotated[User, Depends(get_current_user)],
    weather_client: Annotated[WeatherClient, Depends(get_weather_client)],
    lat: Annotated[float, Query(ge=-90, le=90)],
    lon: Annotated[float, Query(ge=-180, le=180)],
    forecast_time: datetime | None = None,
) -> WeatherPointResponse:
    try:
        return weather_client.get_weather_for_point(lat, lon, forecast_time)
    except WeatherClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Weather API unavailable",
        ) from exc
