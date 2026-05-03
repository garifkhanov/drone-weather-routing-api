import json
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.drone import Drone
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.models.route_waypoint import RouteWaypoint
from app.models.user import User
from app.models.weather_point import WeatherPoint
from app.repositories import drones as drone_repository
from app.repositories import routes as route_repository
from app.schemas.route import (
    RoutePlanRequest,
    RoutePlanResponse,
    RouteWaypointResponse,
    WeatherSummary,
)
from app.services.grid_builder import (
    build_grid,
    find_nearest_grid_position,
)
from app.services.pathfinder import (
    GridNode,
    calculate_effective_distance,
    calculate_path_distance,
    find_path_a_star,
)
from app.services.risk_calculator import (
    calculate_weather_risk,
    is_weather_blocked,
)
from app.services.weather_client import (
    Coordinate,
    WeatherClientError,
    WeatherData,
)


ROUTE_FOUND = "route_found"
ROUTE_NOT_FOUND = "route_not_found"


class RoutePlannerError(RuntimeError):
    pass


class DroneNotFoundError(RoutePlannerError):
    pass


class RoutePlanningWeatherError(RoutePlannerError):
    pass


class RoutePlanningValidationError(RoutePlannerError):
    pass


class WeatherClientProtocol(Protocol):
    def get_hourly_weather_for_points(
        self,
        points: Sequence[Coordinate],
        forecast_time: datetime,
    ) -> list[WeatherData]:
        pass


class RoutePlanner:
    def __init__(
        self,
        db: Session,
        weather_client: WeatherClientProtocol,
    ) -> None:
        self.db = db
        self.weather_client = weather_client

    def plan_route(
        self,
        current_user: User,
        route_data: RoutePlanRequest,
    ) -> RoutePlanResponse:
        drone = drone_repository.get_user_drone(
            self.db,
            current_user.id,
            route_data.drone_id,
        )

        if drone is None:
            raise DroneNotFoundError("Drone not found")

        route_request = route_repository.create_route_request(
            self.db,
            current_user.id,
            route_data,
        )

        start = Coordinate(route_data.start_lat, route_data.start_lon)
        end = Coordinate(route_data.end_lat, route_data.end_lon)

        try:
            coordinate_grid = build_grid(
                start,
                end,
                route_data.grid_size,
                route_data.corridor_width_km,
            )
        except ValueError as exc:
            self._mark_request_failed(route_request.id)
            raise RoutePlanningValidationError(str(exc)) from exc

        flat_points = [
            coordinate
            for row in coordinate_grid
            for coordinate in row
        ]
        try:
            weather_data = self._get_weather_data(flat_points, route_data)
        except RoutePlanningWeatherError:
            self._mark_request_failed(route_request.id)
            raise
        weather_by_position = self._save_weather_points(
            route_request.id,
            coordinate_grid,
            weather_data,
            drone,
        )
        node_grid = self._build_node_grid(coordinate_grid, weather_by_position)
        start_position = find_nearest_grid_position(coordinate_grid, start)
        goal_position = find_nearest_grid_position(coordinate_grid, end)
        path = find_path_a_star(node_grid, start_position, goal_position)
        weather_summary = self._build_weather_summary(weather_data)

        if path is None:
            return self._save_not_found_result(
                route_request.id,
                reason="No valid path found within weather and range constraints",
                explanation=[
                    "Some grid cells were blocked due to wind or precipitation",
                    "A* search could not find a connected path through the grid",
                ],
                weather_summary=weather_summary,
            )

        total_distance_km = calculate_path_distance(path)
        effective_distance_km = calculate_effective_distance(path)
        risk_score = self._calculate_path_risk(path)

        if effective_distance_km > drone.max_range_km:
            return self._save_not_found_result(
                route_request.id,
                reason="Route exceeds drone maximum range.",
                explanation=[
                    "A weather-valid path was found",
                    "Effective distance exceeds the drone maximum range",
                ],
                weather_summary=weather_summary,
                total_distance_km=total_distance_km,
                effective_distance_km=effective_distance_km,
                risk_score=risk_score,
            )

        route_result = self._create_route_result(
            route_request_id=route_request.id,
            status=ROUTE_FOUND,
            explanation=[
                "Route found using A* search on weather risk grid",
                "The route avoids points with excessive wind or precipitation",
                "Effective distance is within drone range",
            ],
            total_distance_km=total_distance_km,
            effective_distance_km=effective_distance_km,
            risk_score=risk_score,
        )
        self._save_waypoints(route_result.id, path)
        self._mark_request_completed(route_request.id)

        return RoutePlanResponse(
            status=ROUTE_FOUND,
            route_request_id=route_request.id,
            route_result_id=route_result.id,
            total_distance_km=round(total_distance_km, 2),
            effective_distance_km=round(effective_distance_km, 2),
            risk_score=round(risk_score, 3),
            weather_summary=weather_summary,
            route=[
                RouteWaypointResponse(
                    lat=node.coordinate.lat,
                    lon=node.coordinate.lon,
                    weather_risk=round(node.weather_risk, 3),
                )
                for node in path
            ],
            explanation=json.loads(route_result.explanation),
        )

    def _get_weather_data(
        self,
        points: list[Coordinate],
        route_data: RoutePlanRequest,
    ) -> list[WeatherData]:
        try:
            weather_data = self.weather_client.get_hourly_weather_for_points(
                points,
                route_data.departure_time,
            )
        except WeatherClientError as exc:
            raise RoutePlanningWeatherError("Weather API unavailable") from exc

        if len(weather_data) != len(points):
            raise RoutePlanningWeatherError(
                "Weather API returned incomplete forecast data",
            )

        return weather_data

    def _save_weather_points(
        self,
        route_request_id: int,
        coordinate_grid: Sequence[Sequence[Coordinate]],
        weather_data: Sequence[WeatherData],
        drone: Drone,
    ) -> dict[tuple[int, int], WeatherPoint]:
        weather_by_position: dict[tuple[int, int], WeatherPoint] = {}
        weather_iterator = iter(weather_data)

        for row_index, row in enumerate(coordinate_grid):
            for column_index, _ in enumerate(row):
                weather = next(weather_iterator)
                risk_score = calculate_weather_risk(weather, drone)
                is_blocked = is_weather_blocked(weather, drone)
                weather_point = WeatherPoint(
                    route_request_id=route_request_id,
                    lat=weather.coordinate.lat,
                    lon=weather.coordinate.lon,
                    forecast_time=weather.forecast_time,
                    wind_speed_ms=weather.wind_speed_ms,
                    wind_gust_ms=weather.wind_gust_ms,
                    precipitation_mm=weather.precipitation_mm,
                    weather_code=weather.weather_code,
                    risk_score=risk_score,
                    is_blocked=is_blocked,
                )
                self.db.add(weather_point)
                weather_by_position[(row_index, column_index)] = weather_point

        self.db.commit()
        return weather_by_position

    @staticmethod
    def _build_node_grid(
        coordinate_grid: Sequence[Sequence[Coordinate]],
        weather_by_position: dict[tuple[int, int], WeatherPoint],
    ) -> list[list[GridNode]]:
        node_grid: list[list[GridNode]] = []

        for row_index, row in enumerate(coordinate_grid):
            node_row: list[GridNode] = []
            for column_index, coordinate in enumerate(row):
                weather_point = weather_by_position[(row_index, column_index)]
                node_row.append(
                    GridNode(
                        row=row_index,
                        column=column_index,
                        coordinate=coordinate,
                        weather_risk=weather_point.risk_score,
                        is_blocked=weather_point.is_blocked,
                    ),
                )
            node_grid.append(node_row)

        return node_grid

    def _save_not_found_result(
        self,
        route_request_id: int,
        reason: str,
        explanation: list[str],
        weather_summary: WeatherSummary,
        total_distance_km: float | None = None,
        effective_distance_km: float | None = None,
        risk_score: float | None = None,
    ) -> RoutePlanResponse:
        route_result = self._create_route_result(
            route_request_id=route_request_id,
            status=ROUTE_NOT_FOUND,
            explanation=explanation,
            total_distance_km=total_distance_km,
            effective_distance_km=effective_distance_km,
            risk_score=risk_score,
            reason=reason,
        )
        self._mark_request_failed(route_request_id)

        return RoutePlanResponse(
            status=ROUTE_NOT_FOUND,
            route_request_id=route_request_id,
            route_result_id=route_result.id,
            total_distance_km=self._round_optional(total_distance_km, 2),
            effective_distance_km=self._round_optional(effective_distance_km, 2),
            risk_score=self._round_optional(risk_score, 3),
            weather_summary=weather_summary,
            route=[],
            reason=reason,
            explanation=explanation,
        )

    def _create_route_result(
        self,
        route_request_id: int,
        status: str,
        explanation: list[str],
        total_distance_km: float | None = None,
        effective_distance_km: float | None = None,
        risk_score: float | None = None,
        reason: str | None = None,
    ) -> RouteResult:
        route_result = RouteResult(
            route_request_id=route_request_id,
            status=status,
            total_distance_km=total_distance_km,
            effective_distance_km=effective_distance_km,
            risk_score=risk_score,
            reason=reason,
            explanation=json.dumps(explanation),
        )
        self.db.add(route_result)
        self.db.commit()
        self.db.refresh(route_result)
        return route_result

    def _save_waypoints(
        self,
        route_result_id: int,
        path: Sequence[GridNode],
    ) -> None:
        for sequence_number, node in enumerate(path, start=1):
            self.db.add(
                RouteWaypoint(
                    route_result_id=route_result_id,
                    sequence_number=sequence_number,
                    lat=node.coordinate.lat,
                    lon=node.coordinate.lon,
                    weather_risk=node.weather_risk,
                ),
            )

        self.db.commit()

    def _mark_request_completed(self, route_request_id: int) -> None:
        self._update_route_request_status(route_request_id, "completed")

    def _mark_request_failed(self, route_request_id: int) -> None:
        self._update_route_request_status(route_request_id, "failed")

    def _update_route_request_status(
        self,
        route_request_id: int,
        status: str,
    ) -> None:
        route_request = self.db.get(RouteRequest, route_request_id)

        if route_request is not None:
            route_request.status = status
            self.db.commit()

    @staticmethod
    def _calculate_path_risk(path: Sequence[GridNode]) -> float:
        if not path:
            return 0.0
        return sum(node.weather_risk for node in path) / len(path)

    @staticmethod
    def _build_weather_summary(
        weather_data: Sequence[WeatherData],
    ) -> WeatherSummary:
        return WeatherSummary(
            max_wind_speed_ms=max(
                weather.wind_speed_ms for weather in weather_data
            ),
            max_gust_ms=max(weather.wind_gust_ms for weather in weather_data),
            max_precipitation_mm=max(
                weather.precipitation_mm for weather in weather_data
            ),
        )

    @staticmethod
    def _round_optional(value: float | None, digits: int) -> float | None:
        if value is None:
            return None
        return round(value, digits)
