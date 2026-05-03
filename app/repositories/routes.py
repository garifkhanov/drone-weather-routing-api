from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.models.route_waypoint import RouteWaypoint
from app.schemas.route import RouteRequestCreate


def create_route_request(
    db: Session,
    user_id: int,
    route_data: RouteRequestCreate,
) -> RouteRequest:
    route_request = RouteRequest(
        user_id=user_id,
        status="created",
        **route_data.model_dump(),
    )
    db.add(route_request)
    db.commit()
    db.refresh(route_request)
    return route_request


def get_user_route_requests(db: Session, user_id: int) -> list[RouteRequest]:
    statement = (
        select(RouteRequest)
        .where(RouteRequest.user_id == user_id)
        .order_by(RouteRequest.id)
    )
    return list(db.scalars(statement).all())


def get_user_route_request(
    db: Session,
    user_id: int,
    route_request_id: int,
) -> RouteRequest | None:
    statement = select(RouteRequest).where(
        RouteRequest.id == route_request_id,
        RouteRequest.user_id == user_id,
    )
    return db.scalar(statement)


def delete_route_request(db: Session, route_request: RouteRequest) -> None:
    db.delete(route_request)
    db.commit()


def get_user_route_result(
    db: Session,
    user_id: int,
    route_result_id: int,
) -> RouteResult | None:
    statement = (
        select(RouteResult)
        .join(RouteRequest)
        .where(
            RouteResult.id == route_result_id,
            RouteRequest.user_id == user_id,
        )
    )
    return db.scalar(statement)


def get_route_result_waypoints(
    db: Session,
    user_id: int,
    route_result_id: int,
) -> list[RouteWaypoint] | None:
    route_result = get_user_route_result(db, user_id, route_result_id)

    if route_result is None:
        return None

    statement = (
        select(RouteWaypoint)
        .where(RouteWaypoint.route_result_id == route_result_id)
        .order_by(RouteWaypoint.sequence_number)
    )
    return list(db.scalars(statement).all())
