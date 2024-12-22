import functools
import itertools
from functools import cache
from typing import Iterable

from common.line_solver import LineSolver, create_summing_solution

LineDataType = tuple[str, int]

_NUM_KEYPAD_LAYOUT = """789,456,123,X0A"""
_ARROW_KEYPAD_LAYOUT = """X^A,<v>"""
_LAYOUTS = (_NUM_KEYPAD_LAYOUT, _ARROW_KEYPAD_LAYOUT, _ARROW_KEYPAD_LAYOUT)


def parse_line(line: str) -> LineDataType:
    line = line.strip()
    return line, int(line[:-1])


@cache
def _compute_pos_lookup_table(keypad_layout: str) -> dict[str, tuple[int, int]]:
    return {
        col_val: (row_idx, col_idx)
        for row_idx, row_val in enumerate(keypad_layout.split(','))
        for col_idx, col_val in enumerate(row_val)
    }


@cache
def _compute_all_movements_between_keys(src_key: str, dst_key: str, keypad: str) -> Iterable[str]:
    pos_lookup = _compute_pos_lookup_table(keypad)
    src_pos, dst_pos = pos_lookup[src_key], pos_lookup[dst_key]
    unreachable_pos = pos_lookup['X']
    row_diff, col_diff = (dst_i - src_i for src_i, dst_i in zip(src_pos, dst_pos))

    row_char = '^' if row_diff < 0 else 'v'
    col_char = '<' if col_diff < 0 else '>'
    row_first_str = (row_char * abs(row_diff)) + (col_char * abs(col_diff))
    col_first_str = (col_char * abs(col_diff)) + (row_char * abs(row_diff))
    all_possible_movements = set(''.join(s) for s in itertools.permutations(row_first_str))
    if src_pos[0] == unreachable_pos[0] and dst_pos[1] == unreachable_pos[1]:
        all_possible_movements.discard(col_first_str)
    elif src_pos[1] == unreachable_pos[1] and dst_pos[0] == unreachable_pos[0]:
        all_possible_movements.discard(row_first_str)
    return tuple(s + 'A' for s in all_possible_movements)


def _expand_numeric_seq(seq: str) -> Iterable[str]:
    input_seq = itertools.chain('A', seq)
    output_seq_opts = [
        _compute_all_movements_between_keys(src, dst, _NUM_KEYPAD_LAYOUT)
        for src, dst in itertools.pairwise(input_seq)
    ]
    return (''.join(sub_seqs) for sub_seqs in itertools.product(*output_seq_opts))


@cache
def _count_arrow_keypad_options(seq_options: tuple[str, ...], depth: int) -> int:
    """
    Given an iterable of arrow keypad sequences which all represent the same underlying key presses,
    count the minimum number button presses necessary to expand any of those sequences.
    """
    if depth == 0:
        return min(len(s) for s in seq_options)

    return min(
        sum(
            _count_arrow_keypad_options(
                _compute_all_movements_between_keys(new_src, new_dst, _ARROW_KEYPAD_LAYOUT),
                depth - 1,
            )
            for new_src, new_dst in itertools.pairwise(itertools.chain('A', seq_option))
        )
        for seq_option in seq_options
    )


def compute_code_complexity(line_data: LineDataType, robot_count: int) -> int:
    sequence, numeric_val = line_data
    seq_options = _expand_numeric_seq(sequence)
    return _count_arrow_keypad_options(seq_options, robot_count) * numeric_val


if __name__ == "__main__":
    LineSolver[LineDataType, None].construct_for_day(
        day_number=21,
        line_parser=parse_line,
        solutions=[
            create_summing_solution(functools.partial(compute_code_complexity, robot_count=2)),
            create_summing_solution(functools.partial(compute_code_complexity, robot_count=25)),
        ],
    ).solve_all()
