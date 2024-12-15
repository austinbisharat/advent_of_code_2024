import math
from typing import Sequence, Callable

from common.line_solver import LineSolver, create_summing_solution

LineDataType = tuple[int, Sequence[int]]


def parse_line(line: str) -> LineDataType:
    line = line.strip()
    target, rest = line.split(":")
    seq = rest.strip().split(" ")
    return int(target), tuple(map(int, seq))


def pt1_line_score(line: LineDataType) -> int:
    return score_line(
        line,
        [
            lambda a, b: a + b,
            lambda a, b: a * b,
        ],
    )


def score_line(line: LineDataType, operators: list[Callable[[int, int], int]]) -> int:
    target, values = line
    if not _can_score_target(target, values[0], remaining=values[1:], operators=operators):
        return 0

    return target


def _can_score_target(
    target: int,
    cur_val: int,
    remaining: Sequence[int],
    operators: list[Callable[[int, int], int]],
) -> bool:
    if len(remaining) == 0:
        return cur_val == target

    return any(
        _can_score_target(target, op(cur_val, remaining[0]), remaining[1:], operators)
        for op in operators
    )


def pt2_line_score(line: LineDataType) -> int:
    return score_line(
        line,
        [
            lambda a, b: a + b,
            lambda a, b: a * b,
            concat_ints,
        ]
    )


def concat_ints(a: int, b: int) -> int:
    return a * (10 ** math.ceil(math.log10(b + 1))) + b


if __name__ == "__main__":
    print(concat_ints(23, 100))
    LineSolver[LineDataType, None].construct_for_day(
        day_number=7,
        line_parser=parse_line,
        solutions=[
            create_summing_solution(pt1_line_score),
            create_summing_solution(pt2_line_score),
        ]
    ).solve_all()
