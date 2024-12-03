from typing import *
from collections import Counter

from common.parsing_helpers import load_numeric_grid
from common.file_solver import FileSolver


LoadedDataType = tuple[tuple[int], tuple[int]]


def load_lists(file: TextIO) -> LoadedDataType:
    return cast(LoadedDataType, tuple(zip(*load_numeric_grid(file))))


def compute_list_diff(data: LoadedDataType) -> int:
    left, right = data
    result = 0
    for l, r in zip(sorted(left), sorted(right)):
        result += abs(l-r)
    return result


def compute_similarity(data: LoadedDataType) -> int:
    left, right = data
    counts = Counter(right)
    result = 0
    for elem in left:
        result += counts[elem] * elem
    return result


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=1,
        loader=load_lists,
        solutions=[compute_list_diff, compute_similarity]
    ).solve_all()
