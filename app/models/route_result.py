from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.route_request import RouteRequest
    from app.models.route_waypoint import RouteWaypoint


class RouteResult(Base):
    __tablename__ = "route_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_request_id: Mapped[int] = mapped_column(
        ForeignKey("route_requests.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    total_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    effective_distance_km: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explanation: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    route_request: Mapped["RouteRequest"] = relationship(
        back_populates="route_result",
    )
    waypoints: Mapped[list["RouteWaypoint"]] = relationship(
        back_populates="route_result",
        cascade="all, delete-orphan",
    )
