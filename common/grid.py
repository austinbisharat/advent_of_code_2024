import collections
import enum
import itertools
from typing import Generic, TypeVar, Sequence, TextIO, cast, Optional, Iterable, Callable, Self, Hashable, Protocol

from common.graph_search import GraphSearcher

T = TypeVar('T')


class InvalidPointException(Exception):
    pass


class InvalidMazeException(Exception):
    pass


PositionType = tuple[int, int]


class Direction(enum.Enum):
    # Sensitive to order -- must
    NORTH = (-1, 0)
    NORTH_EAST = (-1, 1)
    EAST = (0, 1)
    SOUTH_EAST = (1, 1)
    SOUTH = (1, 0)
    SOUTH_WEST = (1, -1)
    WEST = (0, -1)
    NORTH_WEST = (-1, -1)


ALL_DIRECTIONS = list(Direction)
CARDINAL_DIRS = [d for d in Direction if sum(map(abs, d.value)) == 1]
POSITIVE_DIRS = [d for d in Direction if all(val >= 0 for val in d.value)]


def add_point(left: PositionType, right: PositionType) -> PositionType:
    return cast(PositionType, tuple(l + r for l, r in zip(left, right)))


class Grid(Generic[T]):
    def __init__(self, grid: Sequence[Sequence[T]]) -> None:
        self._grid = [
            list(row)
            for row in grid
        ]
        self.height = len(grid)
        self.width = 0
        if self.height > 0:
            for row in self._grid[1:]:
                assert len(row) == len(self._grid[0])
            self.width = len(grid[0])

    @classmethod
    def create_empty_grid(cls, height: int, width: int) -> 'Grid[Optional[T]]':
        return Grid([[None for _ in range(width)] for _ in range(height)])

    def is_valid_point(self, point: PositionType) -> bool:
        row, col = point
        return 0 <= row < self.height and 0 <= col < self.width

    def __getitem__(self, point: PositionType) -> T:
        if not self.is_valid_point(point):
            raise InvalidPointException(f'Invalid point {point}. Width: {self.width}, Height: {self.height}')
        row, col = point
        return self._grid[row][col]

    def __setitem__(self, point: PositionType, value: T) -> None:
        if not self.is_valid_point(point):
            raise InvalidPointException(f'Invalid point {point}')

        row, col = point
        self._grid[row][col] = value

    def iter_points(
        self,
        row_order_asc: bool = True,
        col_order_asc: bool = True,
    ) -> Iterable[PositionType]:
        return itertools.product(
            range(self.height) if row_order_asc else reversed(range(self.height)),
            range(self.width) if col_order_asc else reversed(range(self.width)),
        )

    def iter_points_and_values(
        self,
        row_order_asc: bool = True,
        col_order_asc: bool = True,
    ) -> Iterable[tuple[PositionType, T]]:
        return ((p, self[p]) for p in self.iter_points(row_order_asc, col_order_asc))

    def __iter__(self) -> Iterable[tuple[PositionType, T]]:
        return self.iter_points_and_values()

    def iter_neighboring_points(
        self,
        point: PositionType,
        directions: Sequence['Direction'] = tuple(CARDINAL_DIRS),
    ) -> Iterable[PositionType]:
        all_neighbors = (
            add_relative_point(point, direction.value)
            for direction in directions
        )
        return (
            neighbor
            for neighbor in all_neighbors
            if self.is_valid_point(neighbor)
        )

    def iter_neighboring_points_and_values(
        self,
        point: PositionType,
        directions: Sequence['Direction'] = tuple(CARDINAL_DIRS),
    ) -> Iterable[tuple[PositionType, T]]:
        return (
            (neighbor_point, self[neighbor_point])
            for neighbor_point in self.iter_neighboring_points(point, directions)
        )

    def dimensions(self) -> tuple[int, int]:
        return self.height, self.width

    def format_str(self, format_val: Callable[[T], str] = str) -> str:
        return '\n'.join(
            ''.join(format_val(self[row_idx, col_idx]) for col_idx in range(self.width))
            for row_idx in range(self.height)
        )


class SparseGrid(Grid[T]):
    def __init__(
        self,
        dimensions: tuple[int, int],
        values: dict[PositionType, T],
        default_value: T,
    ) -> None:
        super().__init__([])
        self._sparse_grid = dict(values)
        self.height, self.width = dimensions
        self._default_value = default_value

    def __getitem__(self, point: PositionType) -> T:
        if not self.is_valid_point(point):
            raise InvalidPointException(f'Invalid point {point}. Width: {self.width}, Height: {self.height}')
        return self._sparse_grid.get(point, self._default_value)

    def __setitem__(self, point: PositionType, value: Optional[T]) -> None:
        if not self.is_valid_point(point):
            raise InvalidPointException(f'Invalid point {point}')
        self._sparse_grid[point] = value


class MazeCellProtocol(Protocol):
    def is_terminal(self) -> bool:
        ...

    def is_travelable_point(self) -> bool:
        ...


CellType = TypeVar('CellType', bound=[MazeCellProtocol, Hashable])


class MazeCell(enum.Enum):
    EMPTY = '.'
    WALL = '#'
    START = 'S'
    END = 'E'

    def is_terminal(self) -> bool:
        return self == self.END

    def is_travelable_point(self) -> bool:
        return self != self.WALL


class MazeGrid(Grid[CellType], GraphSearcher[PositionType]):
    def __init__(
        self,
        grid_data: Sequence[Sequence[T]],
    ) -> None:
        super().__init__(grid_data)
        super(Grid, self).__init__()
        self._grid_cell_type_to_positions = collections.defaultdict(set)
        for location, cell in self.iter_points_and_values():
            self._grid_cell_type_to_positions[cell].add(location)

    def get_locations_by_cell_value(self, cell_type: CellType) -> set[PositionType]:
        return self._grid_cell_type_to_positions[cell_type]

    def get_location_by_cell_type(self, cell_type: CellType) -> PositionType:
        locations = self._grid_cell_type_to_positions[cell_type]
        if len(locations) != 1:
            raise InvalidMazeException(f'Invalid cell type {cell_type}')
        return next(iter(locations))

    @classmethod
    def parse_grid_from_file(
        cls,
        file: TextIO,
        cell_parser: Callable[[str], CellType],
    ) -> Self:
        grid_data = [
            [cell_parser(cell) for cell in row.strip()]
            for row in file.readlines()
            if row.strip()
        ]
        return cls(grid_data)

    def get_neighbors(self, node: PositionType) -> Iterable[PositionType]:
        return (
            neighbor
            for neighbor, cell in self.iter_neighboring_points_and_values(node)
            if cell.is_travelable_point()
        )

    def edge_weight(self, orig: PositionType, neighbor: PositionType) -> float:
        return 1

    def is_terminal_node(self, node: PositionType) -> bool:
        return self[node].is_terminal()


def load_char_grid(file: TextIO) -> Grid[str]:
    return Grid([l.strip() for l in file.readlines() if l])


def load_digit_grid(file: TextIO) -> Grid[int]:
    return Grid([
        list(map(int, line.strip()))
        for line in file.readlines()
        if line.strip()
    ])


def scale_relative_point(point: (int, int), scale: int) -> (int, int):
    return tuple(scale * cord for cord in point)


def add_relative_point(point: tuple[int, int], other_point: tuple[int, int]) -> tuple[int, int]:
    return cast(tuple[int, int], tuple(x + y for x, y in zip(point, other_point)))


def subtract_relative_point(point: tuple[int, int], other_point: tuple[int, int]):
    return cast(tuple[int, int], tuple(x - y for x, y in zip(point, other_point)))


def rotate_90(d: Direction, turns: int = 1) -> 'Direction':
    idx = CARDINAL_DIRS.index(d)
    if idx == -1:
        raise IndexError(f'Invalid direction {d}')
    return CARDINAL_DIRS[(idx + turns) % len(CARDINAL_DIRS)]


def manhattan_distance(a: PositionType, b: PositionType) -> int:
    return sum(abs(a_i - b_i) for a_i, b_i in zip(a, b))
