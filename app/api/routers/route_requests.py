from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.route_request import RouteRequest
from app.models.user import User
from app.repositories import drones as drone_repository
from app.repositories import routes as route_repository
from app.schemas.route import RouteRequestCreate, RouteRequestResponse


router = APIRouter(prefix="/route-requests", tags=["route requests"])


def get_route_request_or_404(
    db: Session,
    user_id: int,
    route_request_id: int,
) -> RouteRequest:
    route_request = route_repository.get_user_route_request(
        db,
        user_id,
        route_request_id,
    )

    if route_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route request not found",
        )

    return route_request


@router.post(
    "",
    response_model=RouteRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_route_request(
    route_data: RouteRequestCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RouteRequestResponse:
    drone = drone_repository.get_user_drone(db, current_user.id, route_data.drone_id)

    if drone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )

    return route_repository.create_route_request(db, current_user.id, route_data)


@router.get("", response_model=list[RouteRequestResponse])
def list_route_requests(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[RouteRequestResponse]:
    return route_repository.get_user_route_requests(db, current_user.id)


@router.get("/{route_request_id}", response_model=RouteRequestResponse)
def get_route_request(
    route_request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RouteRequestResponse:
    return get_route_request_or_404(db, current_user.id, route_request_id)


@router.delete("/{route_request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route_request(
    route_request_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    route_request = get_route_request_or_404(
        db,
        current_user.id,
        route_request_id,
    )
    route_repository.delete_route_request(db, route_request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
