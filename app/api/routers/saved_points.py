from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.saved_point import SavedPoint
from app.models.user import User
from app.repositories import saved_points as saved_point_repository
from app.schemas.saved_point import (
    SavedPointCreate,
    SavedPointResponse,
    SavedPointUpdate,
)


router = APIRouter(prefix="/saved-points", tags=["saved-points"])


def get_owned_saved_point_or_404(
    db: Session,
    user_id: int,
    saved_point_id: int,
) -> SavedPoint:
    saved_point = saved_point_repository.get_user_saved_point(
        db,
        user_id,
        saved_point_id,
    )

    if saved_point is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved point not found",
        )

    return saved_point


@router.post(
    "",
    response_model=SavedPointResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_saved_point(
    point_data: SavedPointCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SavedPointResponse:
    return saved_point_repository.create_saved_point(db, current_user.id, point_data)


@router.get("", response_model=list[SavedPointResponse])
def list_saved_points(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SavedPointResponse]:
    return saved_point_repository.get_user_saved_points(db, current_user.id)


@router.get("/{saved_point_id}", response_model=SavedPointResponse)
def get_saved_point(
    saved_point_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SavedPointResponse:
    return get_owned_saved_point_or_404(db, current_user.id, saved_point_id)


@router.patch("/{saved_point_id}", response_model=SavedPointResponse)
def update_saved_point(
    saved_point_id: int,
    point_data: SavedPointUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SavedPointResponse:
    saved_point = get_owned_saved_point_or_404(db, current_user.id, saved_point_id)
    return saved_point_repository.update_saved_point(db, saved_point, point_data)


@router.delete("/{saved_point_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_point(
    saved_point_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    saved_point = get_owned_saved_point_or_404(db, current_user.id, saved_point_id)
    saved_point_repository.delete_saved_point(db, saved_point)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
