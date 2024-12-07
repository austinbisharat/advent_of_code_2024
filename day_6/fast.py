import bisect
import itertools
from collections import deque
from typing import TextIO, Optional, Sequence, Iterable

from common.file_solver import FileSolver
from common.grid import Grid, Direction, PositionType, rotate_90

GuardPosType = tuple[PositionType, Direction]

_GUARD_CHAR_TO_DIR = {
    '^': Direction.NORTH,
    '>': Direction.WEST,
    '<': Direction.EAST,
    'v': Direction.SOUTH,
}


class LabGrid(Grid[str]):
    def __init__(self, lab_data: Sequence[Sequence[str]]) -> None:
        super().__init__(lab_data)

        self._obstructions_by_row = [
            [
                col_idx
                for col_idx, col_val in enumerate(row_val)
                if col_val == '#'
            ]
            for row_val in lab_data
        ]
        self._obstructions_by_col = [
            [
                row_idx
                for row_idx in range(self.height)
                if lab_data[row_idx][col_idx] == '#'
            ]
            for col_idx in range(self.width)
        ]

    def __setitem__(self, position: PositionType, value: str) -> None:
        super().__setitem__(position, value)

        row, col = position
        if value == '#':
            # Add our new obstruction to our internal data structures
            bisect.insort(self._obstructions_by_row[row], col)
            bisect.insort(self._obstructions_by_col[col], row)
        else:
            # Filter out our removed obstruction from internal data structures
            self._obstructions_by_row[row] = [c for c in self._obstructions_by_row[row] if c != col]
            self._obstructions_by_col[col] = [r for r in self._obstructions_by_col[col] if r != row]

    def get_sparse_path(self, initial_guard_pos: GuardPosType) -> tuple[Sequence[GuardPosType], bool]:
        path = deque()
        visited_guard_positions: set[GuardPosType] = set()
        cur_guard_pos = initial_guard_pos
        while self.is_valid_point(cur_guard_pos[0]) and cur_guard_pos not in visited_guard_positions:
            path.append(cur_guard_pos)
            visited_guard_positions.add(cur_guard_pos)
            cur_guard_pos = self._get_next_location(cur_guard_pos)
        path.append(cur_guard_pos)
        return list(path), cur_guard_pos in visited_guard_positions

    def _get_next_location(self, guard_pos: GuardPosType) -> GuardPosType:
        (row, col), direction = guard_pos

        sign = sum(direction.value)  # -1 if NORTH or WEST, +1 if SOUTH or EAST
        if direction in {Direction.NORTH, Direction.SOUTH}:
            next_point = (
                self._get_next_dimension_on_axis(
                    current_location_on_axis=row,
                    relevant_obstructions_on_axis=self._obstructions_by_col[col],
                    sign=sign,
                    axis_length=self.height,
                ),
                col,
            )
        else:
            next_point = (
                row,
                self._get_next_dimension_on_axis(
                    current_location_on_axis=col,
                    relevant_obstructions_on_axis=self._obstructions_by_row[row],
                    sign=sign,
                    axis_length=self.height,
                ),
            )

        return next_point, rotate_90(direction)

    @staticmethod
    def _get_next_dimension_on_axis(
            current_location_on_axis: int,
            relevant_obstructions_on_axis: Sequence[int],
            sign: int,
            axis_length: int,
    ) -> int:
        next_obstruction_idx = (
                bisect.bisect(relevant_obstructions_on_axis, current_location_on_axis)
                + ((sign - 1) >> 1)
        )
        if next_obstruction_idx < 0:
            return -1
        elif next_obstruction_idx >= len(relevant_obstructions_on_axis):
            return axis_length
        else:
            return relevant_obstructions_on_axis[next_obstruction_idx] - sign

    def fill_sparse_path(self, path: Sequence[GuardPosType]) -> set[PositionType]:
        visited_positions: set[PositionType] = set()
        for cur, next in itertools.pairwise(path):
            (start_row, start_col), _ = cur
            (end_row, end_col), _ = next
            positions = [
                (row, col)
                for row in self._get_range_for_axis(start_row, end_row, self.height)
                for col in self._get_range_for_axis(start_col, end_col, self.width)
            ]
            visited_positions.update(positions)
        return visited_positions

    @staticmethod
    def _get_range_for_axis(start: int, end: int, axis_length: int) -> Iterable[int]:
        lower_val_on_axis = max(0, min(start, end))
        upper_val_on_axis = min(max(start, end) + 1, axis_length)
        return range(lower_val_on_axis, upper_val_on_axis)


LoadedDataType = tuple[LabGrid, GuardPosType]


def load(file: TextIO) -> LoadedDataType:
    guard_pos: Optional[GuardPosType] = None
    lines = [line.strip() for line in file.readlines() if line.strip()]
    for row, line in enumerate(lines):
        for col, value in enumerate(line.strip()):
            if guard_val := _GUARD_CHAR_TO_DIR.get(value):
                guard_pos = ((row, col), guard_val)

    if guard_pos is None:
        raise ValueError("No Guard pos in file")

    return LabGrid(lines), guard_pos


def solve_pt1(data: LoadedDataType) -> int:
    grid, guard_pos = data
    path, _ = grid.get_sparse_path(guard_pos)
    return len(grid.fill_sparse_path(path))


def solve_pt2(data: LoadedDataType) -> int:
    obstacle_grid, initial_pos = data
    sparse_path, _ = obstacle_grid.get_sparse_path(initial_pos)
    full_path = obstacle_grid.fill_sparse_path(sparse_path)
    result = 0
    for point in full_path:
        if _can_cause_cycle_at(obstacle_grid, initial_pos, point):
            # print(point)
            result += 1
    return result


def _can_cause_cycle_at(obstacle_grid: LabGrid, initial_pos: GuardPosType, new_obstacle_pos: PositionType) -> bool:
    if new_obstacle_pos == initial_pos[0]:
        return False
    obstacle_grid[new_obstacle_pos] = '#'
    _, is_cycle = obstacle_grid.get_sparse_path(initial_pos)
    obstacle_grid[new_obstacle_pos] = '.'
    return is_cycle


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=6,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
