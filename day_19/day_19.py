from typing import TextIO, Sequence, Iterable

from common.line_solver import LineSolver, AbstractLineByLineSolution
from common.trie import Trie

FileConfigType = Sequence[str]
LineDataType = str


def pare_file_config(file: TextIO) -> FileConfigType:
    towels = [t.strip() for t in file.readline().strip().split(',')]
    file.readline()
    return towels


def parse_line(line: str) -> LineDataType:
    return line.strip()


class OnsenTowelSolver(AbstractLineByLineSolution[LineDataType, FileConfigType]):
    def __init__(self) -> None:
        self._towel_trie = Trie()
        self._num_possible_towels = 0

    def load_config(self, config: FileConfigType) -> None:
        for towel in config:
            self._towel_trie.insert(towel[::-1])

    def process_line(self, possible_towel: LineDataType) -> None:
        towel_len = len(possible_towel)

        sub_towel_dp_arr = [0] * (towel_len + 1)
        sub_towel_dp_arr[0] = 1

        for i in range(1, towel_len + 1):
            # the first i characters reversed
            reverse_towel_prefix = possible_towel[i - 1::-1]
            sub_towel_dp_arr[i] = self._aggregate_towels(
                sub_towel_dp_arr[i - len(prefix)]
                for prefix in self._towel_trie.iter_all_matching_words(reverse_towel_prefix)
            )

        self._num_possible_towels += sub_towel_dp_arr[-1]

    @classmethod
    def _aggregate_towels(cls, towel_vals: Iterable[int]) -> int:
        return int(any(towel_vals))

    def result(self) -> int:
        return self._num_possible_towels


class OnsenTowelEveryOptionSolver(OnsenTowelSolver):
    def _aggregate_towels(self, towel_vals: Iterable[int]) -> int:
        return sum(towel_vals)


if __name__ == "__main__":
    LineSolver[LineDataType, FileConfigType].construct_for_day(
        day_number=19,
        line_parser=parse_line,
        file_config_parser=pare_file_config,
        solutions=[OnsenTowelSolver, OnsenTowelEveryOptionSolver]
    ).solve_all()
