import enum
from typing import Generic, TypeVar, Sequence, TextIO, cast, Optional

T = TypeVar('T')


class InvalidPoint(Exception):
    pass


PositionType = tuple[int, int]


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
            raise InvalidPoint(f'Invalid point {point}. Width: {self.width}, Height: {self.height}')
        row, col = point
        return self._grid[row][col]

    def __setitem__(self, point: PositionType, value: T) -> None:
        if not self.is_valid_point(point):
            raise InvalidPoint(f'Invalid point {point}')

        row, col = point
        self._grid[row][col] = value


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


CARDINAL_DIRS = [d for d in Direction if sum(map(abs, d.value)) == 1]
POSITIVE_DIRS = [d for d in Direction if all(val >= 0 for val in d.value)]


def rotate_90(d: Direction, turns: int = 1) -> 'Direction':
    idx = CARDINAL_DIRS.index(d)
    if idx == -1:
        raise IndexError(f'Invalid direction {d}')
    return CARDINAL_DIRS[(idx + turns) % len(CARDINAL_DIRS)]
