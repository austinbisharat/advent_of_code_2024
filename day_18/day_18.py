import collections
import itertools
from typing import TextIO, Tuple, cast, Iterable, Sequence

from common.file_solver import FileSolver
from common.graph_search import GraphSearcher, NodeType
from common.grid import Grid, PositionType, SparseGrid, ALL_DIRECTIONS, manhattan_distance

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
        return manhattan_distance(node, self._goal())


def solve_pt1(data: LoadedDataType) -> int:
    dimensions, corrupted_locs, cutoff = data
    first_kb = {
        loc: True
        for loc in corrupted_locs[:cutoff]
    }
    grid = SparseGrid[bool](dimensions, first_kb, default_value=False)
    _, cost = MemorySearcher(grid).get_best_path((0, 0))
    return int(cost)


class CorruptedMemoryManager:
    def __init__(self, dimensions: tuple[int, int]) -> None:
        self._grid = SparseGrid[bool](dimensions, {}, default_value=False)

        self._cluster_id_generator = itertools.count()
        self._top_right_cluster = next(self._cluster_id_generator)
        self._bottom_left_cluster = next(self._cluster_id_generator)

        self._corrupted_pts_to_cluster_id: dict[PositionType, int] = {}
        self._cluster_id_to_corrupted_pts: dict[int, set[PositionType]] = collections.defaultdict(set)

        self._path_unreachable = False

    def iter_corrupted_neighbors(self, point: PositionType) -> Iterable[PositionType]:
        return (
            neighbor
            for neighbor, neighbor_val in
            self._grid.iter_neighboring_points_and_values(point, directions=ALL_DIRECTIONS)
            if neighbor_val
        )

    def add_corrupted_memory(self, point: PositionType) -> bool:
        """
        If corrupting the given point causes the bottom right location to be unreachable, return true. Otherwise,
        return false.
        """
        if self._path_unreachable:
            return True

        self._grid[point] = True
        neighboring_clusters = {
            self._corrupted_pts_to_cluster_id[n]
            for n in self.iter_corrupted_neighbors(point)
        }

        cluster_id = self._get_cluster_id(point, neighboring_clusters)
        self._corrupted_pts_to_cluster_id[point] = cluster_id
        self._cluster_id_to_corrupted_pts[cluster_id].add(point)
        neighboring_clusters.add(cluster_id)
        self._merge_clusters(neighboring_clusters)

        self._path_unreachable = self._top_right_cluster == self._bottom_left_cluster
        return self._path_unreachable

    def _get_cluster_id(self, point: PositionType, neighboring_clusters: set[int]) -> int:
        row, col = point
        height, width = self._grid.dimensions()
        if row == height - 1 or col == 0:
            return self._bottom_left_cluster

        if row == 0 or col == width - 1:
            return self._top_right_cluster

        if neighboring_clusters:
            return min(neighboring_clusters)

        return next(self._cluster_id_generator)

    def _merge_clusters(self, cluster_ids: set[int]) -> None:
        if len(cluster_ids) <= 1:
            return

        new_cid = max(cluster_ids, key=lambda cid: len(self._cluster_id_to_corrupted_pts[cid]))

        for old_cid in cluster_ids:
            if old_cid == new_cid:
                continue
            for point in self._cluster_id_to_corrupted_pts[old_cid]:
                self._cluster_id_to_corrupted_pts[new_cid].add(point)
                self._corrupted_pts_to_cluster_id[point] = new_cid
            del self._cluster_id_to_corrupted_pts[old_cid]

        if self._top_right_cluster in cluster_ids:
            self._top_right_cluster = new_cid
        if self._bottom_left_cluster in cluster_ids:
            self._bottom_left_cluster = new_cid


def solve_pt2(data: LoadedDataType) -> str:
    dimensions, corrupted_locs, _ = data
    manager = CorruptedMemoryManager(dimensions)
    for corrupted_loc in corrupted_locs:
        result = manager.add_corrupted_memory(corrupted_loc)
        if result:
            return ','.join(map(str, reversed(corrupted_loc)))
    return 'No sol'


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=18,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
