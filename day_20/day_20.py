import collections
import itertools
import typing
from timeit import timeit
from typing import TextIO

from common.file_solver import FileSolver
from common.grid import MazeGrid, MazeCell, PositionType, add_relative_point, manhattan_distance


class MazeConfig(typing.NamedTuple):
    short_cheat_threshold: int
    long_cheat_threshold: int


LoadedDataType = tuple[MazeGrid, MazeConfig]


def load(file: TextIO) -> LoadedDataType:
    thresholds = MazeConfig(*map(int, file.readline().strip().split(',')))
    return MazeGrid[MazeCell].parse_grid_from_file(file, MazeCell), thresholds


def solve_pt1(data: LoadedDataType) -> int:
    maze_grid, maze_config = data
    solver = MazeCheatSolver(maze_grid)
    total_count, counts_by_savings = solver.count_cheats_by_savings_threshold(
        max_cheat_duration=2,
        cheat_savings_threshold=maze_config.long_cheat_threshold,
    )
    return total_count


def solve_pt2(data: LoadedDataType) -> int:
    maze_grid, maze_config = data
    solver = MazeCheatSolver(maze_grid)
    total_count, counts_by_savings = solver.count_cheats_by_savings_threshold(
        max_cheat_duration=20,
        cheat_savings_threshold=maze_config.long_cheat_threshold,
    )
    return total_count


class MazeCheatSolver:
    class _Cheat(typing.NamedTuple):
        start: PositionType
        end: PositionType
        savings: int

    def __init__(self, maze: MazeGrid[MazeCell]) -> None:
        self._maze = maze
        self._start_node = maze.get_location_by_cell_type(MazeCell.START)
        self._end_node = maze.get_location_by_cell_type(MazeCell.END)
        self._node_to_dist_from_start = maze.get_all_travel_costs_starting_at_node(self._start_node)
        self._node_to_dist_from_end = maze.get_all_travel_costs_starting_at_node(self._end_node)
        self._no_cheat_cost = int(self._node_to_dist_from_start[self._end_node])

    def count_cheats_by_savings_threshold(
        self,
        max_cheat_duration: int,
        cheat_savings_threshold: int,
    ) -> tuple[int, dict[int, int]]:
        num_cheats_above_threshold = 0
        cheat_counts_by_savings_threshold = collections.defaultdict(int)

        for cell_loc, cell_val in self._maze.iter_points_and_values():
            if cell_val == MazeCell.WALL:
                continue
            cheats = self._get_cheats_for_starting_point(
                cheat_start=cell_loc,
                max_cheat_duration=max_cheat_duration,
                cheat_savings_threshold=cheat_savings_threshold,
            )
            num_cheats_above_threshold += len(cheats)
            for cheat in cheats:
                cheat_counts_by_savings_threshold[cheat.savings] += 1
        return num_cheats_above_threshold, cheat_counts_by_savings_threshold

    def _get_cheats_for_starting_point(
        self,
        cheat_start: PositionType,
        max_cheat_duration: int,
        cheat_savings_threshold: int,
    ) -> set[_Cheat]:
        potential_cheat_end = self._iter_bound_points_within_dist(cheat_start, max_cheat_duration)
        cheats = (
            self._compute_cheat(cheat_start, cheat_end)
            for cheat_end in potential_cheat_end
            if self._maze[cheat_end] != MazeCell.WALL
        )
        return {
            cheat for cheat in cheats if cheat.savings >= cheat_savings_threshold
        }

    def _compute_cheat(self, cheat_start: PositionType, cheat_end: PositionType) -> _Cheat:
        total_path_cost = sum((
            self._node_to_dist_from_start[cheat_start],
            self._node_to_dist_from_end[cheat_end],
            manhattan_distance(cheat_start, cheat_end)
        ))
        savings = self._no_cheat_cost - total_path_cost
        return MazeCheatSolver._Cheat(cheat_start, cheat_end, savings)

    def _iter_bound_points_within_dist(self, point: PositionType, distance: int) -> typing.Iterable[PositionType]:
        return [
            p
            for p in self._iter_unbound_points_within_dist(point, distance)
            if self._maze.is_valid_point(p)
        ]

    def _iter_unbound_points_within_dist(self, point: PositionType, distance: int) -> typing.Iterable[PositionType]:
        for i in range(1, distance + 1):
            for j in range(i + 1):
                for row_mult, col_mult in itertools.product((-1, 1), (-1, 1)):
                    yield add_relative_point(point, (row_mult * j, col_mult * (i - j)))
                    yield add_relative_point(point, (row_mult * (i - j), col_mult * j))


if __name__ == "__main__":
    solver = FileSolver[MazeGrid[MazeCell]].construct_for_day(
        day_number=20,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    )
    print('=' * 80 + f'\nTime taken: {timeit(lambda: solver.solve_all(), number=1):0.4} seconds')
