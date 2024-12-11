import math
from typing import TextIO, Sequence

from common.file_solver import FileSolver
from common.parsing_helpers import split_nums

LoadedDataType = Sequence[int]


def load(file: TextIO) -> LoadedDataType:
    return split_nums(file.read().strip())


def num_digits(num: int) -> int:
    return math.floor(math.log10(num)) + 1


def count_rock_expansion(initial_rocks: Sequence[int], num_steps: int = 25) -> int:
    memo: dict[tuple[int, int], int] = dict()

    def get_expansion_count(rock_number: int, num_steps: int) -> int:
        if num_steps == 0:
            return 1

        if result := memo.get((rock_number, num_steps)):
            return result

        if rock_number == 0:
            return get_expansion_count(1, num_steps - 1)

        dig_count = num_digits(rock_number)
        if dig_count % 2 == 0:
            divisor = 10 ** (dig_count // 2)
            result = (
                get_expansion_count(rock_number % divisor, num_steps - 1)
                + get_expansion_count(rock_number // divisor, num_steps - 1)
            )
            memo[(rock_number, num_steps)] = result
            return result

        result = get_expansion_count(rock_number * 2024, num_steps - 1)
        memo[(rock_number, num_steps)] = result
        return result

    return sum(get_expansion_count(rock_number, num_steps) for rock_number in initial_rocks)


def solve_pt1(data: LoadedDataType) -> int:
    return count_rock_expansion(data, 25)


def solve_pt2(data: LoadedDataType) -> int:
    return count_rock_expansion(data, 75)


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=11,
        loader=load,
        solutions=[count_rock_expansion, solve_pt2]
    ).solve_all()
