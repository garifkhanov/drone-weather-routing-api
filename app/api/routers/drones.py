from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.drone import Drone
from app.models.user import User
from app.repositories import drones as drone_repository
from app.schemas.drone import DroneCreate, DroneResponse, DroneUpdate


router = APIRouter(prefix="/drones", tags=["drones"])


def get_owned_drone_or_404(
    db: Session,
    owner_id: int,
    drone_id: int,
) -> Drone:
    drone = drone_repository.get_user_drone(db, owner_id, drone_id)

    if drone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drone not found",
        )

    return drone


@router.post(
    "",
    response_model=DroneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_drone(
    drone_data: DroneCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DroneResponse:
    return drone_repository.create_drone(db, current_user.id, drone_data)


@router.get("", response_model=list[DroneResponse])
def list_drones(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[DroneResponse]:
    return drone_repository.get_user_drones(db, current_user.id)


@router.get("/{drone_id}", response_model=DroneResponse)
def get_drone(
    drone_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DroneResponse:
    return get_owned_drone_or_404(db, current_user.id, drone_id)


@router.patch("/{drone_id}", response_model=DroneResponse)
def update_drone(
    drone_id: int,
    drone_data: DroneUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DroneResponse:
    drone = get_owned_drone_or_404(db, current_user.id, drone_id)
    return drone_repository.update_drone(db, drone, drone_data)


@router.delete("/{drone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_drone(
    drone_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    drone = get_owned_drone_or_404(db, current_user.id, drone_id)
    drone_repository.delete_drone(db, drone)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
