from timeit import timeit

import fast
from day_6 import *


def fast_solve() -> None:
    FileSolver[fast.LoadedDataType].construct_for_day(
        day_number=6,
        loader=fast.load,
        solutions=[fast.solve_pt1, fast.solve_pt2],
        log_func=lambda x: ...,
    ).solve_all()


def slow_solve() -> None:
    FileSolver[LoadedDataType].construct_for_day(
        day_number=6,
        loader=load,
        solutions=[solve_pt1, solve_pt2],
        log_func=lambda x: ...,
    ).solve_all()


if __name__ == "__main__":
    fast = timeit(fast_solve, number=10)
    slow = timeit(slow_solve, number=10)
    print(f'Fast: {fast:.2}s, slow: {slow:.2}s. Speedup: {slow / fast:.4}x')
