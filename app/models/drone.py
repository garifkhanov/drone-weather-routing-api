from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.route_request import RouteRequest
    from app.models.user import User


class Drone(Base):
    __tablename__ = "drones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    max_range_km: Mapped[float] = mapped_column(Float, nullable=False)
    max_wind_speed_ms: Mapped[float] = mapped_column(Float, nullable=False)
    max_gust_ms: Mapped[float] = mapped_column(Float, nullable=False)
    max_precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False)
    cruise_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="drones")
    route_requests: Mapped[list["RouteRequest"]] = relationship(
        back_populates="drone",
    )
