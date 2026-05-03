from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_weather_client
from app.models.user import User
from app.repositories import routes as route_repository
from app.schemas.route import (
    RoutePlanRequest,
    RoutePlanResponse,
    RouteResultResponse,
    RouteWaypointResponse,
)
from app.services.route_planner import (
    DroneNotFoundError,
    RoutePlanner,
    RoutePlanningValidationError,
    RoutePlanningWeatherError,
)
from app.services.weather_client import WeatherClient


router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/plan", response_model=RoutePlanResponse)
def plan_route(
    route_data: RoutePlanRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    weather_client: Annotated[WeatherClient, Depends(get_weather_client)],
) -> RoutePlanResponse:
    planner = RoutePlanner(db, weather_client)

    try:
        return planner.plan_route(current_user, route_data)
    except DroneNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        ) from exc
    except RoutePlanningValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RoutePlanningWeatherError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Weather API unavailable",
        ) from exc


@router.get("/results/{route_result_id}", response_model=RouteResultResponse)
def get_route_result(
    route_result_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RouteResultResponse:
    route_result = route_repository.get_user_route_result(
        db,
        current_user.id,
        route_result_id,
    )

    if route_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route result not found",
        )

    return route_result


@router.get(
    "/results/{route_result_id}/waypoints",
    response_model=list[RouteWaypointResponse],
)
def get_route_result_waypoints(
    route_result_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[RouteWaypointResponse]:
    waypoints = route_repository.get_route_result_waypoints(
        db,
        current_user.id,
        route_result_id,
    )

    if waypoints is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route result not found",
        )

    return waypoints
