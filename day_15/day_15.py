import enum
import itertools
from collections import deque
from typing import TextIO, Sequence, ClassVar, Type

from common.file_solver import FileSolver
from common.grid import Grid, Direction, add_relative_point, PositionType, scale_relative_point

_log_func = lambda msg: ...


class GridSpace(enum.Enum):
    WALL = '#'
    EMPTY = '.'
    BOX = 'O'
    ROBOT = '@'

    LEFT_BOX = '['
    RIGHT_BOX = ']'


_STR_VAL_TO_DIRECTION = {
    '^': Direction.NORTH,
    'v': Direction.SOUTH,
    '<': Direction.WEST,
    '>': Direction.EAST,
}


class _CannotMakeGridSpaceException(Exception):
    pass


class WHGrid(Grid[GridSpace]):
    _SCORABLE_CELL_TYPE: ClassVar[GridSpace] = GridSpace.BOX

    def __init__(self, data: Sequence[Sequence[str]]) -> None:
        self._robot_loc = (0, 0)

        parsed_grid = deque()
        for i, row in enumerate(data):
            parsed_row = deque()
            for j, cell in enumerate(row):
                parsed_cell = GridSpace(cell)
                parsed_row.append(parsed_cell)
                if parsed_cell == GridSpace.ROBOT:
                    self._robot_loc = (i, j)
            parsed_grid.append(parsed_row)
        super().__init__(parsed_grid)

    def move_robot_step(self, direction: Direction) -> None:
        new_robot_loc = add_relative_point(self._robot_loc, direction.value)
        for i in itertools.count(1):
            loc = add_relative_point(self._robot_loc, scale_relative_point(direction.value, i))
            if not self.is_valid_point(loc) or self[loc] == GridSpace.WALL:
                return

            if self[loc] == GridSpace.EMPTY:
                # swap any potential boxes with the first empty space to make room for the robot
                self[new_robot_loc], self[loc] = self[loc], self[new_robot_loc]
                self[new_robot_loc], self[self._robot_loc] = self[self._robot_loc], self[new_robot_loc]
                self._robot_loc = new_robot_loc
                return

    def __str__(self) -> str:
        return '\n'.join(
            ''.join(cell.value for cell in row)
            for row in self._grid
        )

    def score(self) -> int:
        return sum(
            row_idx * 100 + col_idx
            for (row_idx, col_idx), cell in self.iter_points_and_values()
            if cell == self._SCORABLE_CELL_TYPE
        )


class WideWHGrid(WHGrid):
    _SCORABLE_CELL_TYPE: ClassVar[GridSpace] = GridSpace.LEFT_BOX

    def __init__(self, data: Sequence[Sequence[str]]) -> None:
        self._robot_loc = (0, 0)

        parsed_grid = deque()
        for i, row in enumerate(data):
            parsed_row = deque()
            for j, cell in enumerate(row):
                parsed_cell = GridSpace(cell)
                if parsed_cell == GridSpace.ROBOT:
                    self._robot_loc = (i, j * 2)
                    parsed_row.append(GridSpace.ROBOT)
                    parsed_row.append(GridSpace.EMPTY)
                elif parsed_cell == GridSpace.BOX:
                    parsed_row.append(GridSpace.LEFT_BOX)
                    parsed_row.append(GridSpace.RIGHT_BOX)
                else:
                    parsed_row.append(parsed_cell)
                    parsed_row.append(parsed_cell)

            parsed_grid.append(parsed_row)
        super(WHGrid, self).__init__(parsed_grid)

    def move_robot_step(self, direction: Direction) -> None:
        new_robot_loc = add_relative_point(self._robot_loc, direction.value)
        try:
            self._ensure_space({new_robot_loc}, direction)
        except _CannotMakeGridSpaceException:
            return
        self[new_robot_loc], self[self._robot_loc] = self[self._robot_loc], self[new_robot_loc]
        self._robot_loc = new_robot_loc

    def _ensure_space(self, locations: set[PositionType], direction: Direction) -> None:
        if len(locations) == 0:
            return

        next_locations = set()
        for loc in locations:
            if not self.is_valid_point(loc) or self[loc] == GridSpace.WALL:
                raise _CannotMakeGridSpaceException()

            if self[loc] not in (GridSpace.LEFT_BOX, GridSpace.RIGHT_BOX):
                continue

            next_locations.add(add_relative_point(loc, direction.value))
            if direction in (Direction.NORTH, Direction.SOUTH):
                other_box_loc = (
                    add_relative_point(loc, Direction.EAST.value)
                    if self[loc] == GridSpace.LEFT_BOX
                    else add_relative_point(loc, Direction.WEST.value)
                )
                next_locations.add(add_relative_point(other_box_loc, direction.value))

        self._ensure_space(next_locations, direction)

        for next_loc in next_locations:
            prev_loc = add_relative_point(next_loc, scale_relative_point(direction.value, -1))
            self[next_loc], self[prev_loc] = self[prev_loc], self[next_loc]


def load_wh(file: TextIO, grid_cls: Type[WHGrid] = WHGrid) -> tuple[WHGrid, Sequence[Direction]]:
    file_data = file.read()
    grid_data, direction_data = file_data.split('\n\n')

    grid = grid_cls(grid_data.split('\n'))
    directions = [_STR_VAL_TO_DIRECTION[d] for d in direction_data if d in _STR_VAL_TO_DIRECTION]
    return grid, directions


def load_wide_wh(file: TextIO) -> tuple[WHGrid, Sequence[Direction]]:
    return load_wh(file, WideWHGrid)


def solve(data: tuple[WHGrid, Sequence[Direction]]) -> int:
    wh_grid, robot_directions = data

    for robot_dir in robot_directions:
        _log_func(wh_grid)
        _log_func(robot_dir)
        _log_func(robot_dir)
        wh_grid.move_robot_step(robot_dir)

    _log_func(wh_grid)
    _log_func(wh_grid)

    return wh_grid.score()


if __name__ == "__main__":
    print('=' * 80)
    print('PT1:\n')
    FileSolver[tuple[WHGrid, Sequence[Direction]]].construct_for_day(
        day_number=15,
        loader=load_wh,
        solutions=[solve]
    ).solve_all()

    print('=' * 80)
    print('PT2:\n')
    FileSolver[tuple[WHGrid, Sequence[Direction]]].construct_for_day(
        day_number=15,
        loader=load_wide_wh,
        solutions=[solve]
    ).solve_all()
