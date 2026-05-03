import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from app.services.grid_builder import haversine_distance_km
from app.services.weather_client import Coordinate


GridPosition = tuple[int, int]


@dataclass(frozen=True)
class GridNode:
    row: int
    column: int
    coordinate: Coordinate
    weather_risk: float
    is_blocked: bool


def find_path_a_star(
    grid: Sequence[Sequence[GridNode]],
    start_position: GridPosition,
    goal_position: GridPosition,
) -> list[GridNode] | None:
    if not _is_valid_position(grid, start_position):
        return None
    if not _is_valid_position(grid, goal_position):
        return None

    start_node = _get_node(grid, start_position)
    goal_node = _get_node(grid, goal_position)

    if start_node.is_blocked or goal_node.is_blocked:
        return None

    open_heap: list[tuple[float, int, GridPosition]] = []
    heap_counter = 0
    came_from: dict[GridPosition, GridPosition] = {}
    g_score: dict[GridPosition, float] = {start_position: 0.0}
    visited: set[GridPosition] = set()

    heapq.heappush(open_heap, (0.0, heap_counter, start_position))

    while open_heap:
        _, _, current_position = heapq.heappop(open_heap)

        if current_position in visited:
            continue

        if current_position == goal_position:
            return reconstruct_path(came_from, current_position, grid)

        visited.add(current_position)
        current_node = _get_node(grid, current_position)

        for neighbor in get_neighbors(grid, current_position):
            neighbor_position = (neighbor.row, neighbor.column)
            edge_cost = _calculate_edge_cost(current_node, neighbor)
            tentative_g_score = g_score[current_position] + edge_cost

            if tentative_g_score >= g_score.get(neighbor_position, float("inf")):
                continue

            came_from[neighbor_position] = current_position
            g_score[neighbor_position] = tentative_g_score
            heuristic = haversine_distance_km(
                neighbor.coordinate,
                goal_node.coordinate,
            )
            f_score = tentative_g_score + heuristic
            heap_counter += 1
            heapq.heappush(
                open_heap,
                (f_score, heap_counter, neighbor_position),
            )

    return None


def reconstruct_path(
    came_from: dict[GridPosition, GridPosition],
    current_position: GridPosition,
    grid: Sequence[Sequence[GridNode]],
) -> list[GridNode]:
    path = [_get_node(grid, current_position)]

    while current_position in came_from:
        current_position = came_from[current_position]
        path.append(_get_node(grid, current_position))

    path.reverse()
    return path


def get_neighbors(
    grid: Sequence[Sequence[GridNode]],
    position: GridPosition,
) -> list[GridNode]:
    row, column = position
    neighbors: list[GridNode] = []

    for row_delta in (-1, 0, 1):
        for column_delta in (-1, 0, 1):
            if row_delta == 0 and column_delta == 0:
                continue

            neighbor_position = (row + row_delta, column + column_delta)
            if not _is_valid_position(grid, neighbor_position):
                continue

            neighbor = _get_node(grid, neighbor_position)
            if not neighbor.is_blocked:
                neighbors.append(neighbor)

    return neighbors


def calculate_path_distance(path: Sequence[GridNode]) -> float:
    return sum(
        haversine_distance_km(previous.coordinate, current.coordinate)
        for previous, current in zip(path, path[1:])
    )


def calculate_effective_distance(path: Sequence[GridNode]) -> float:
    return sum(
        _calculate_edge_cost(previous, current)
        for previous, current in zip(path, path[1:])
    )


def _calculate_edge_cost(start_node: GridNode, end_node: GridNode) -> float:
    distance_km = haversine_distance_km(
        start_node.coordinate,
        end_node.coordinate,
    )
    average_weather_risk = (
        start_node.weather_risk + end_node.weather_risk
    ) / 2
    return distance_km * (1 + average_weather_risk)


def _is_valid_position(
    grid: Sequence[Sequence[GridNode]],
    position: GridPosition,
) -> bool:
    row, column = position
    return (
        0 <= row < len(grid)
        and 0 <= column < len(grid[row])
    )


def _get_node(
    grid: Sequence[Sequence[GridNode]],
    position: GridPosition,
) -> GridNode:
    row, column = position
    return grid[row][column]
