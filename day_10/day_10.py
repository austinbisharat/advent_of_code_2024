from typing import Callable

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
    memo = Grid[Optional[T]].create_empty_grid(terrain.height, terrain.width)

    def get_scorable_value_for_point(point: PositionType) -> T:
        if memo[point] is not None:
            return memo[point]

        if terrain[point] == 9:
            memo[point] = get_terminal_value(point)
            return memo[point]

        terminals = reducer(
            get_scorable_value_for_point(neighbor_point)
            for neighbor_point, neighbor_value in terrain.iter_neighboring_points_and_values(point)
            if terrain.is_valid_point(neighbor_point) and neighbor_value == terrain[point] + 1
        )

        memo[point] = terminals
        return terminals

    return sum(
        score_function(get_scorable_value_for_point(point))
        for point, terrain_at_point in terrain
        if terrain_at_point == 0
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
