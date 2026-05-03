from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.route_result import RouteResult


class RouteWaypoint(Base):
    __tablename__ = "route_waypoints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_result_id: Mapped[int] = mapped_column(
        ForeignKey("route_results.id"),
        index=True,
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    weather_risk: Mapped[float] = mapped_column(Float, nullable=False)

    route_result: Mapped["RouteResult"] = relationship(
        back_populates="waypoints",
    )
