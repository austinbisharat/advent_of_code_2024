import enum
import itertools
from collections import deque
from typing import TextIO, Sequence, NamedTuple, Iterable

from common import graph_search
from common.file_solver import FileSolver
from common.grid import Grid, Direction, PositionType, add_relative_point, rotate_90


class GridCell(enum.Enum):
    WALL = '#'
    EMPTY = '.'
    START = 'S'
    END = 'E'


class ReindeerPosition(NamedTuple):
    row: int
    col: int
    direction: Direction

    def raw_position(self) -> PositionType:
        return self[:2]

    def next_reindeer_position(self) -> 'ReindeerPosition':
        new_row, new_col = add_relative_point(self.raw_position(), self.direction.value)
        return ReindeerPosition(new_row, new_col, self.direction)


class ReindeerMaze(Grid[str]):
    def __init__(self, grid_data: Sequence[Sequence[str]]) -> None:
        self._start_loc = ReindeerPosition(0, 0, Direction.EAST)
        self._end_loc = ReindeerPosition(0, 0, Direction.EAST)

        parsed_grid = deque()
        for i, row in enumerate(grid_data):
            parsed_row = deque()
            for j, cell in enumerate(row):
                parsed_cell = GridCell(cell)
                parsed_row.append(parsed_cell)
                if parsed_cell == GridCell.START:
                    self._start_loc = ReindeerPosition(i, j, Direction.EAST)
                elif parsed_cell == GridCell.END:
                    self._end_loc = ReindeerPosition(i, j, Direction.EAST)
            parsed_grid.append(parsed_row)

        super().__init__(parsed_grid)

    def neighbors(self, orig: ReindeerPosition) -> Iterable[ReindeerPosition]:
        positions = [
            ReindeerPosition(orig.row, orig.col, rotate_90(orig.direction, turns=1)),
            ReindeerPosition(orig.row, orig.col, rotate_90(orig.direction, turns=3))
        ]
        next_pos = orig.next_reindeer_position()
        next_raw_position = next_pos.raw_position()
        if self.is_valid_point(next_raw_position) and self[next_raw_position] in (GridCell.EMPTY, GridCell.END):
            # yield next_pos
            positions.append(next_pos)
        return positions

    @property
    def start_loc(self) -> ReindeerPosition:
        return self._start_loc

    @property
    def end_loc(self) -> ReindeerPosition:
        return self._end_loc


class ReindeerSolver(graph_search.GraphSearcher[ReindeerPosition]):
    def __init__(self, maze: ReindeerMaze) -> None:
        super().__init__()
        self._maze = maze

    def edge_weight(self, orig: ReindeerPosition, neighbor: ReindeerPosition) -> float:
        if orig.direction != neighbor.direction:
            return 1000
        return 1

    def get_neighbors(self, node: ReindeerPosition) -> Iterable[ReindeerPosition]:
        return self._maze.neighbors(node)

    def heuristic(self, current: ReindeerPosition) -> float:
        row_dist = abs(current.row - self._maze.end_loc.row)
        col_dist = abs(current.col - self._maze.end_loc.row)
        has_turns = 1000 if row_dist or col_dist else 0
        return row_dist + col_dist + has_turns

    def is_terminal_node(self, current: ReindeerPosition) -> bool:
        return current.raw_position() == self._maze.end_loc.raw_position()


def load(file: TextIO) -> ReindeerMaze:
    return ReindeerMaze([l.strip() for l in file.readlines() if l.strip()])


def solve(maze: ReindeerMaze) -> str:
    solver = ReindeerSolver(maze)
    paths, score = solver.get_all_best_paths(maze.start_loc)

    uniq_nodes = {
        reindeer_pos.raw_position()
        for reindeer_pos in itertools.chain.from_iterable(paths)
    }
    return f'Best path score: {int(score)}, num_nodes: {len(uniq_nodes)}'


if __name__ == "__main__":
    FileSolver[ReindeerMaze].construct_for_day(
        day_number=16,
        loader=load,
        solutions=[solve]
    ).solve_all()
