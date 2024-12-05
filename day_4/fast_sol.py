import collections
import itertools
from typing import Sequence

from common.line_solver import LineSolver, AbstractLineByLineSolution

LineDataType = Sequence[str]
DirType = tuple[int, int]


class FastXMASWordSolver(AbstractLineByLineSolution[LineDataType]):
    _WORD = 'XMAS'
    _DIRS: Sequence[DirType] = ((1, 0), (1, 1), (0, 1), (1, -1))

    def __init__(self) -> None:
        assert len(self._WORD) == len(set(self._WORD))
        self._result = 0
        self._target_words: tuple[str, str] = self._WORD, self._WORD[::-1]
        self._target_length = len(self._WORD)
        # This dict is a bit hairy to understand. It is intended to store the progress we've
        # made constructing each target word in every possible direction for each position in
        # the last processed line. In particular:
        # - Keys are a tuple of:
        #   - The target word
        #   - The index of the char in the last processed line
        #   - The direction (east, southeast, or south, represented as (0, 1), (1, 1), (1, 0))
        # - Values represent the number of matching characters we've seen so far for target word ending at
        #   the target index in the last line where the target word is oriented in the target direction
        #
        # For example, the entry ('XMAS', 5, (1, 0)) -> 2 would indicate that on the last line at index 5
        # we saw an 'M' (the second char of 'XMAS'), and the line before that must have had an 'X' at
        # index 5 as well.
        self._prev_counts: dict[tuple[str, int, DirType], int] = collections.defaultdict(int)

    def process_line(self, line: LineDataType) -> None:
        cur_counts: dict[tuple[str, int, DirType], int] = collections.defaultdict(int)
        indexable_counts = (self._prev_counts, cur_counts)
        for i, ch in enumerate(line):
            for target_word, target_dir in itertools.product(self._target_words, self._DIRS):
                relative_row, relative_col = target_dir
                prev_value = indexable_counts[1 - relative_row][(target_word, i - relative_col, target_dir)]
                if target_word[prev_value] == ch:
                    next_value = prev_value + 1
                elif ch == target_word[0]:
                    next_value = 1
                else:
                    next_value = 0

                if next_value == len(target_word):
                    next_value = 0
                    self._result += 1
                cur_counts[(target_word, i, target_dir)] = next_value

        self._prev_counts = cur_counts

    def result(self) -> str | int:
        return self._result


class FastCrossMasWordSolver(AbstractLineByLineSolution[LineDataType]):
    class CrossConfig(int):
        _CHARS = 'MS'

        def get_expected_value_at_relative_pos(self, pos: tuple[int, int]) -> str:
            if pos == (0, 0):
                return 'A'
            x, y = (pos[0] + 1) >> 1, (pos[1] + 1) >> 1
            cur_diagonal = x ^ y
            left_diag_idx = self % 2
            right_diag_idx = (self // 2)
            idx = (right_diag_idx & cur_diagonal) | (left_diag_idx ^ cur_diagonal)
            print(
                f'pos: {pos} idx: {idx}, cur_diagonal: {cur_diagonal}, left_diag_idx: {left_diag_idx}, right_diag_idx: {right_diag_idx}')
            return self._CHARS[idx ^ x]

    def __init__(self) -> None:
        self._result = 0
        self._prev_counts: dict[str, int] = collections.defaultdict(int)

    def process_line(self, line: LineDataType) -> None:
        pass

    def result(self) -> str | int:
        return self._result


if __name__ == '__main__':
    solver = LineSolver[LineDataType].construct_for_day(
        day_number=4,
        line_parser=lambda x: x.strip(),
        solutions=[FastXMASWordSolver],
    )
    solver.solve_all()
