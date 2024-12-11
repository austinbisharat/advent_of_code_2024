import itertools
from typing import Callable, Iterable

from common.file_solver import FileSolver
from common.grid import *

LoadedDataType = Grid[int]

T = TypeVar('T')


def _score_terrain(
        terrain: Grid[int],
        get_terminal_value: Callable[[PositionType], T],
        reducer: Callable[[Iterable[T]], T],
        score_function: Callable[[T], int],
) -> int:
    reachable_terminals = Grid[Optional[T]].create_empty_grid(terrain.height, terrain.width)

    def get_reachable_terminals_for_point(point: PositionType) -> T:
        if reachable_terminals[point] is not None:
            return reachable_terminals[point]

        if terrain[point] == 9:
            reachable_terminals[point] = get_terminal_value(point)
            return reachable_terminals[point]

        all_neighbors = (
            add_relative_point(point, direction.value)
            for direction in CARDINAL_DIRS
        )

        terminals = reducer(
            get_reachable_terminals_for_point(neighbor)
            for neighbor in all_neighbors
            if terrain.is_valid_point(neighbor) and terrain[neighbor] == terrain[point] + 1
        )

        reachable_terminals[point] = terminals
        return terminals

    return sum(
        score_function(get_reachable_terminals_for_point(point))
        for point in itertools.product(range(terrain.height), range(terrain.width))
        if terrain[point] == 0
    )


def solve_pt1(data: LoadedDataType) -> int:
    return _score_terrain(
        terrain=data,
        get_terminal_value=lambda point: {point},
        reducer=lambda nested_iterable: set(itertools.chain(*nested_iterable)),
        score_function=len
    )


def solve_pt2(data: LoadedDataType) -> int:
    return _score_terrain(
        terrain=data,
        get_terminal_value=lambda _: 1,
        reducer=sum,
        score_function=lambda score: score,
    )


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=10,
        loader=load_digit_grid,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()