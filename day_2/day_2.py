import itertools
from common.file_solver import FileSolver
from common.line_solver import LineSolver, SummingLineByLineSolution
from common.parsing_helpers import load_numeric_grid, split_nums
from itertools import pairwise


LineDataType = list[int]


def is_basic_seq_safe(seq: list[int]) -> bool:
    if len(seq) <= 1:
        return True

    multiplier = 1 if seq[0] < seq[1] else -1

    def is_safe_pair(a: int, b: int) -> bool:
        return 1 <= multiplier * (b - a) <= 3

    return all(
        is_safe_pair(a, b)
        for a, b in pairwise(seq)
    )


def is_dampened_seq_safe(seq: list[int]) -> bool:
    def coerce_to_sign(val) -> int:
        return val // abs(val) if val != 0 else 0

    if len(seq) <= 2:
        return True

    asc_count = sum(
        coerce_to_sign(cur-prev)
        for prev, cur in pairwise(seq)
    )
    if abs(asc_count) < len(seq) - 3:
        # we're not clearly ascending, nor are we clearly descending. It's
        # impossible to construct a safe sequence
        return False

    # +1 if we expect the seq to ascend, -1 if we expect the seq to descend,
    # and 0 if either might be possible. The only scenario where 0 can happen
    # (and we haven't early returned above) is if the seq is exactly 3 long
    asc_sign = coerce_to_sign(asc_count)

    def is_safe_pair(prev: int, cur: int) -> bool:
        diff = cur - prev
        if asc_sign == 0:
            return 1 <= abs(diff) <= 3
        return 1 <= diff * asc_sign <= 3

    def is_safe_pair_idx(prev_idx: int, cur_idx: int) -> bool:
        if prev_idx < 0 or cur_idx >= len(seq):
            return True
        return is_safe_pair(seq[prev_idx], seq[cur_idx])

    unsafe_pair_indices = []
    for i, (prev, cur) in enumerate(pairwise(seq)):
        if not is_safe_pair(prev, cur):
            unsafe_pair_indices.append(i)

    if len(unsafe_pair_indices) > 2:
        return False
    elif len(unsafe_pair_indices) == 2:
        first_idx, second_idx = unsafe_pair_indices[0], unsafe_pair_indices[1]
        if second_idx - first_idx != 1:
            return False
        return is_safe_pair_idx(first_idx, first_idx + 2)
    elif len(unsafe_pair_indices) == 1:
        idx = unsafe_pair_indices[0]
        return is_safe_pair_idx(idx, idx + 2) or is_safe_pair_idx(idx - 1, idx + 1)

    return True


def is_dumb_dampened_seq_safe(seq: list[int]) -> bool:
    return is_basic_seq_safe(seq) or any(
        is_basic_seq_safe(sub_seq)
        for sub_seq in itertools.combinations(seq, len(seq) - 1)
    )


if __name__ == "__main__":
    LineSolver[LineDataType].construct_for_day(
        day_number=2,
        line_parser=split_nums,
        solutions=[
            SummingLineByLineSolution[LineDataType](is_basic_seq_safe),
            SummingLineByLineSolution[LineDataType](is_dumb_dampened_seq_safe),
            SummingLineByLineSolution[LineDataType](is_dampened_seq_safe),
        ]
    ).solve_all()

