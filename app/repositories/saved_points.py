from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.saved_point import SavedPoint
from app.schemas.saved_point import SavedPointCreate, SavedPointUpdate


def create_saved_point(
    db: Session,
    user_id: int,
    point_data: SavedPointCreate,
) -> SavedPoint:
    saved_point = SavedPoint(user_id=user_id, **point_data.model_dump())
    db.add(saved_point)
    db.commit()
    db.refresh(saved_point)
    return saved_point


def get_user_saved_points(db: Session, user_id: int) -> list[SavedPoint]:
    statement = (
        select(SavedPoint)
        .where(SavedPoint.user_id == user_id)
        .order_by(SavedPoint.id)
    )
    return list(db.scalars(statement).all())


def get_user_saved_point(
    db: Session,
    user_id: int,
    saved_point_id: int,
) -> SavedPoint | None:
    statement = select(SavedPoint).where(
        SavedPoint.id == saved_point_id,
        SavedPoint.user_id == user_id,
    )
    return db.scalar(statement)


def update_saved_point(
    db: Session,
    saved_point: SavedPoint,
    point_data: SavedPointUpdate,
) -> SavedPoint:
    update_data = point_data.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(saved_point, field_name, value)

    db.add(saved_point)
    db.commit()
    db.refresh(saved_point)
    return saved_point


def delete_saved_point(db: Session, saved_point: SavedPoint) -> None:
    db.delete(saved_point)
    db.commit()
