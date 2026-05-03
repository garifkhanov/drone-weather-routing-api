import math
from collections.abc import Sequence

from app.services.weather_client import Coordinate


EARTH_RADIUS_KM = 6371.0
KM_PER_DEGREE_LAT = 111.32
MIN_COS_LAT = 0.01


def haversine_distance_km(start: Coordinate, end: Coordinate) -> float:
    start_lat = math.radians(start.lat)
    end_lat = math.radians(end.lat)
    delta_lat = math.radians(end.lat - start.lat)
    delta_lon = math.radians(end.lon - start.lon)

    haversine_value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(start_lat)
        * math.cos(end_lat)
        * math.sin(delta_lon / 2) ** 2
    )
    haversine_value = min(max(haversine_value, 0.0), 1.0)

    central_angle = 2 * math.atan2(
        math.sqrt(haversine_value),
        math.sqrt(1 - haversine_value),
    )
    return EARTH_RADIUS_KM * central_angle


def build_grid(
    start: Coordinate,
    end: Coordinate,
    grid_size: int,
    corridor_width_km: float,
) -> list[list[Coordinate]]:
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")
    if corridor_width_km <= 0:
        raise ValueError("corridor_width_km must be positive")

    converter = _LocalCoordinateConverter(start, end)
    start_x, start_y = converter.to_xy(start)
    end_x, end_y = converter.to_xy(end)
    route_dx = end_x - start_x
    route_dy = end_y - start_y
    route_length = math.hypot(route_dx, route_dy)

    if route_length == 0:
        direction_x, direction_y = 1.0, 0.0
    else:
        direction_x = route_dx / route_length
        direction_y = route_dy / route_length

    perpendicular_x = -direction_y
    perpendicular_y = direction_x

    grid: list[list[Coordinate]] = []
    for row_index in range(grid_size):
        lateral_fraction = row_index / (grid_size - 1)
        lateral_offset_km = (lateral_fraction - 0.5) * corridor_width_km
        row: list[Coordinate] = []

        for column_index in range(grid_size):
            route_fraction = column_index / (grid_size - 1)
            along_route_km = route_fraction * route_length
            x = (
                start_x
                + direction_x * along_route_km
                + perpendicular_x * lateral_offset_km
            )
            y = (
                start_y
                + direction_y * along_route_km
                + perpendicular_y * lateral_offset_km
            )
            row.append(converter.to_coordinate(x, y))

        grid.append(row)

    return grid


def find_nearest_grid_position(
    grid: Sequence[Sequence[Coordinate]],
    target: Coordinate,
) -> tuple[int, int]:
    if not grid or not any(row for row in grid):
        raise ValueError("grid must contain at least one coordinate")

    nearest_position = (0, 0)
    nearest_distance = math.inf

    for row_index, row in enumerate(grid):
        for column_index, point in enumerate(row):
            distance = haversine_distance_km(point, target)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_position = (row_index, column_index)

    return nearest_position


class _LocalCoordinateConverter:
    def __init__(self, start: Coordinate, end: Coordinate) -> None:
        self.mid_lat = (start.lat + end.lat) / 2
        cos_lat = abs(math.cos(math.radians(self.mid_lat)))
        self.km_per_degree_lon = KM_PER_DEGREE_LAT * max(cos_lat, MIN_COS_LAT)

    def to_xy(self, coordinate: Coordinate) -> tuple[float, float]:
        return (
            coordinate.lon * self.km_per_degree_lon,
            coordinate.lat * KM_PER_DEGREE_LAT,
        )

    def to_coordinate(self, x: float, y: float) -> Coordinate:
        lat = y / KM_PER_DEGREE_LAT
        lon = x / self.km_per_degree_lon
        return Coordinate(
            lat=_clamp(lat, -90, 90),
            lon=_normalize_longitude(lon),
        )


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(max(value, minimum), maximum)


def _normalize_longitude(lon: float) -> float:
    return ((lon + 180) % 360) - 180
