from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories import routes as route_repository
from app.schemas.route import RouteResultResponse, RouteWaypointResponse


router = APIRouter(prefix="/routes", tags=["routes"])


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
