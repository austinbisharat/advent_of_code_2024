from typing import Generic, TypeVar, Sequence, TextIO, cast

T = TypeVar('T')


class InvalidPoint(Exception):
    pass


class Grid(Generic[T]):
    def __init__(self, grid: Sequence[Sequence[T]]) -> None:
        self._grid = grid
        self.height = len(grid)
        self.width = 0
        if self.height > 0:
            for row in self._grid[1:]:
                assert len(row) == len(self._grid[0])
            self.width = len(grid[0])

    def is_valid_point(self, point: tuple[int, int]) -> bool:
        row, col = point
        return 0 <= row < self.height and 0 <= col < self.width

    def __getitem__(self, point: tuple[int, int]) -> T:
        if not self.is_valid_point(point):
            raise InvalidPoint(f'Invalid point {point}. Width: {self.width}, Height: {self.height}')
        row, col = point
        return self._grid[row][col]


def load_char_grid(file: TextIO) -> Grid[str]:
    return Grid([l.strip() for l in file.readlines() if l])


def scale_relative_point(point: (int, int), scale: int) -> (int, int):
    return tuple(scale * cord for cord in point)


def add_relative_point(point: tuple[int, int], other_point: tuple[int, int]) -> tuple[int, int]:
    return cast(tuple[int, int], tuple(x + y for x, y in zip(point, other_point)))
