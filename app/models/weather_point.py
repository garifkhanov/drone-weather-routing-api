from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.route_request import RouteRequest


class WeatherPoint(Base):
    __tablename__ = "weather_points"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_request_id: Mapped[int] = mapped_column(
        ForeignKey("route_requests.id"),
        index=True,
        nullable=False,
    )
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    forecast_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    wind_speed_ms: Mapped[float] = mapped_column(Float, nullable=False)
    wind_gust_ms: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False)
    weather_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    route_request: Mapped["RouteRequest"] = relationship(
        back_populates="weather_points",
    )
