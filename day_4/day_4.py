import itertools
from collections import Counter
from typing import Generator

from common.file_solver import FileSolver
from common.grid import Grid, load_char_grid, add_relative_point, scale_relative_point, InvalidPointException

LoadedDataType = Grid[str]

_WORD = 'XMAS'

_DIRECTIONS = [dir for dir in itertools.product((-1, 0, 1), (-1, 0, 1)) if dir != (0, 0)]


def get_word(grid: Grid[str], start_point: tuple[int, int], dir: tuple[int, int], length: int) -> str:
    res = "".join(
        grid[add_relative_point(start_point, scale_relative_point(dir, i))]
        for i in range(length)
    )
    return res


def get_all_words(grid: Grid[str], start_point: tuple[int, int]) -> Generator[str, None, None]:
    for dir in _DIRECTIONS:
        try:
            yield get_word(grid, start_point, dir, len(_WORD))
        except InvalidPointException:
            pass


def is_eq(w: str) -> bool:
    return w == _WORD


def solve_pt1(grid: LoadedDataType) -> int:
    return sum(
        1
        for point in itertools.product(range(grid.width), range(grid.height))
        for word in get_all_words(grid, point)
        if is_eq(word)
    )


def solve_pt2(grid: LoadedDataType) -> int:
    return sum(
        1
        for point in itertools.product(range(1, grid.width - 1), range(1, grid.height - 1))
        if is_valid_x_point(grid, point)
    )


def is_valid_x_point(grid: LoadedDataType, point: tuple[int, int]) -> bool:
    if not grid[point] == 'A':
        return False
    c = Counter(grid[add_relative_point(point, dir)] for dir in itertools.product((-1, 1), (-1, 1)))
    return c['M'] == 2 and c['S'] == 2 and grid[add_relative_point(point, (-1, -1))] != grid[
        add_relative_point(point, (1, 1))]


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=4,
        loader=load_char_grid,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
