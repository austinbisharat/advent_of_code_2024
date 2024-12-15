import enum
import itertools
from collections import deque
from typing import TextIO, Sequence

from common.file_solver import FileSolver
from common.grid import Grid, Direction, add_relative_point, scale_relative_point


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


class WarehouseGrid(Grid[GridSpace]):
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


LoadedDataType = tuple[WarehouseGrid, Sequence[Direction]]


def load(file: TextIO) -> LoadedDataType:
    file_data = file.read()
    grid_data, direction_data = file_data.split('\n\n')

    grid = WarehouseGrid(grid_data.split('\n'))
    directions = [_STR_VAL_TO_DIRECTION[d] for d in direction_data if d in _STR_VAL_TO_DIRECTION]
    return grid, directions


def solve_pt1(data: LoadedDataType) -> int:
    wh_grid, robot_directions = data

    def score_grid(g: WarehouseGrid) -> int:
        return sum(
            row_idx * 100 + col_idx
            for (row_idx, col_idx), cell in g.iter_points_and_values()
            if cell == GridSpace.BOX
        )

    for robot_dir in robot_directions:
        wh_grid.move_robot_step(robot_dir)
        # print(wh_grid)
        # print()

    return score_grid(wh_grid)


def solve_pt2(data: LoadedDataType) -> int:
    return 0


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=15,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
