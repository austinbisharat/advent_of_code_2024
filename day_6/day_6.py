from collections import deque
from typing import TextIO, Optional

from common.file_solver import FileSolver
from common.grid import Grid, Direction, PositionType, add_point, rotate_90

GuardPosType = tuple[PositionType, Direction]

_GUARD_CHAR_TO_DIR = {
    '^': Direction.NORTH,
    '>': Direction.WEST,
    '<': Direction.EAST,
    'v': Direction.SOUTH,
}


class LabGrid(Grid[bool]):
    pass


LoadedDataType = tuple[LabGrid, GuardPosType]


def load(file: TextIO) -> LoadedDataType:
    grid_data = deque()
    guard_pos: Optional[GuardPosType] = None
    for row, line in enumerate(file):
        next_line_data = deque()
        for col, value in enumerate(line.strip()):
            next_line_data.append(value == '#')
            if guard_val := _GUARD_CHAR_TO_DIR.get(value):
                guard_pos = ((row, col), guard_val)
        grid_data.append(list(next_line_data))

    if guard_pos is None:
        raise ValueError("No Guard pos in file")

    return LabGrid(list(grid_data)), guard_pos


def solve_pt1(data: LoadedDataType) -> int:
    visited_squares, _ = _get_path(*data)
    return len(visited_squares)


def _get_path(obstacle_grid: LabGrid, guard_pos: GuardPosType) -> tuple[set[PositionType], bool]:
    # Need two sets since the first includes orientation and the second doesn't.
    # The first set is necessary to detect potential cycles
    visited_guard_positions: set[GuardPosType] = set()
    visited_squares: set[PositionType] = set()

    while obstacle_grid.is_valid_point(guard_pos[0]) and guard_pos not in visited_guard_positions:
        visited_guard_positions.add(guard_pos)
        visited_squares.add(guard_pos[0])
        guard_pos = _get_next_guard_pos(obstacle_grid, guard_pos)

    return visited_squares, guard_pos in visited_guard_positions


def _get_next_guard_pos(obstacle_grid: LabGrid, guard_pos: GuardPosType) -> GuardPosType:
    point, direction = guard_pos
    next_point = add_point(point, direction.value)
    if obstacle_grid.is_valid_point(next_point) and obstacle_grid[next_point]:
        next_dir = rotate_90(direction)
        return point, next_dir
    return next_point, direction


def solve_pt2(data: LoadedDataType) -> int:
    obstacle_grid, guard_pos = data
    visited_squares, _ = _get_path(obstacle_grid, guard_pos)
    result = 0
    for point in visited_squares:
        if _can_cause_cycle_at(obstacle_grid, guard_pos, point):
            # print(point)
            result += 1
    return result


def _can_cause_cycle_at(obstacle_grid: LabGrid, guard_pos: GuardPosType, new_obstacle_pos: PositionType) -> bool:
    if new_obstacle_pos == guard_pos[0]:
        return False
    obstacle_grid[new_obstacle_pos] = True
    _, is_cycle = _get_path(obstacle_grid, guard_pos)
    obstacle_grid[new_obstacle_pos] = False
    return is_cycle


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=6,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
