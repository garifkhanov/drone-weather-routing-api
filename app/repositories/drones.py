from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.drone import Drone
from app.schemas.drone import DroneCreate, DroneUpdate


def create_drone(db: Session, owner_id: int, drone_data: DroneCreate) -> Drone:
    drone = Drone(owner_id=owner_id, **drone_data.model_dump())
    db.add(drone)
    db.commit()
    db.refresh(drone)
    return drone


def get_user_drones(db: Session, owner_id: int) -> list[Drone]:
    statement = (
        select(Drone)
        .where(Drone.owner_id == owner_id)
        .order_by(Drone.id)
    )
    return list(db.scalars(statement).all())


def get_user_drone(db: Session, owner_id: int, drone_id: int) -> Drone | None:
    statement = select(Drone).where(
        Drone.id == drone_id,
        Drone.owner_id == owner_id,
    )
    return db.scalar(statement)


def update_drone(
    db: Session,
    drone: Drone,
    drone_data: DroneUpdate,
) -> Drone:
    update_data = drone_data.model_dump(exclude_unset=True)

    for field_name, field_value in update_data.items():
        setattr(drone, field_name, field_value)

    db.commit()
    db.refresh(drone)
    return drone


def delete_drone(db: Session, drone: Drone) -> None:
    db.delete(drone)
    db.commit()
