from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.drone import Drone
    from app.models.route_result import RouteResult
    from app.models.user import User
    from app.models.weather_point import WeatherPoint


class RouteRequest(Base):
    __tablename__ = "route_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    drone_id: Mapped[int] = mapped_column(
        ForeignKey("drones.id"),
        index=True,
        nullable=False,
    )
    start_lat: Mapped[float] = mapped_column(Float, nullable=False)
    start_lon: Mapped[float] = mapped_column(Float, nullable=False)
    end_lat: Mapped[float] = mapped_column(Float, nullable=False)
    end_lon: Mapped[float] = mapped_column(Float, nullable=False)
    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    grid_size: Mapped[int] = mapped_column(Integer, nullable=False)
    corridor_width_km: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="route_requests")
    drone: Mapped["Drone"] = relationship(back_populates="route_requests")
    weather_points: Mapped[list["WeatherPoint"]] = relationship(
        back_populates="route_request",
        cascade="all, delete-orphan",
    )
    route_result: Mapped["RouteResult | None"] = relationship(
        back_populates="route_request",
        cascade="all, delete-orphan",
        uselist=False,
    )
