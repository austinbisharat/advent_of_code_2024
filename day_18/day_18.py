from typing import TextIO, Tuple, cast, Iterable, Sequence, Optional

from common.file_solver import FileSolver
from common.graph_search import GraphSearcher, NodeType
from common.grid import Grid, PositionType, SparseGrid

LoadedDataType = tuple[PositionType, Sequence[PositionType], int]


def _parse_num_pair(line: str) -> Tuple[int, int]:
    return cast(
        Tuple[int, int],
        tuple(map(int, reversed(line.strip().split(","))))
    )


def load(file: TextIO) -> LoadedDataType:
    width, height, cutoff = map(int, file.readline().strip().split(","))
    corrupted_locs = [
        _parse_num_pair(line)
        for line in file.readlines()
    ]
    return (height, width), corrupted_locs, cutoff


class MemorySearcher(GraphSearcher[PositionType]):
    def __init__(self, grid: Grid[bool]) -> None:
        super().__init__()
        self._grid = grid

    def get_neighbors(self, node: NodeType) -> Iterable[NodeType]:
        for neighbor, neighbor_val in self._grid.iter_neighboring_points_and_values(node):
            if not neighbor_val:
                yield neighbor

    def edge_weight(self, orig: NodeType, neighbor: NodeType) -> float:
        return 1

    def is_terminal_node(self, node: PositionType) -> bool:
        return node == self._goal()

    def _goal(self) -> PositionType:
        height, width = self._grid.dimensions()
        return height - 1, width - 1

    def heuristic(self, node: NodeType) -> float:
        # Manhattan distance
        return sum(abs(goal - dim) for goal, dim in zip(self._goal(), node))


def solve_pt1(data: LoadedDataType) -> int:
    dimensions, corrupted_locs, cutoff = data
    first_kb = {
        loc: True
        for loc in corrupted_locs[:cutoff]
    }
    grid = SparseGrid[Optional[bool]](dimensions, first_kb, default_value=cast(Optional[bool], None))
    print(grid.format_str(lambda v: '#' if v else '.'))
    _, cost = MemorySearcher(grid).get_best_path((0, 0))
    return int(cost)


def solve_pt2(data: LoadedDataType) -> int:
    return 0


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=18,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
