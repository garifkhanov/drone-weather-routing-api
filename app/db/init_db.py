from app.db.base import Base
from app.db.session import engine
from app.models import (
    Drone,
    RouteRequest,
    RouteResult,
    RouteWaypoint,
    User,
    WeatherPoint,
)


REGISTERED_MODELS = (
    User,
    Drone,
    RouteRequest,
    WeatherPoint,
    RouteResult,
    RouteWaypoint,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
