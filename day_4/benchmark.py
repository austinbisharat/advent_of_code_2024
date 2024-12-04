from timeit import timeit

from day_4 import *
from fast_sol import *


def fast_solve() -> None:
    solver = LineSolver[LineDataType].construct_for_day(
        day_number=4,
        line_parser=lambda x: x.strip(),
        solutions=[FastXMASWordSolver],
        log_func=lambda x: ...,
    )
    solver.solve_file('input_4.txt')


def slow_solve() -> None:
    FileSolver[LoadedDataType].construct_for_day(
        day_number=4,
        loader=load_char_grid,
        solutions=[solve_pt1],
        log_func=lambda x: ...,
    ).solve_file('input_4.txt')


if __name__ == "__main__":
    fast = timeit(fast_solve, number=10)
    slow = timeit(slow_solve, number=10)
    print(f'Fast: {fast:.2}s, slow: {slow:.2}s. Speedup: {slow / fast:.4}x')
