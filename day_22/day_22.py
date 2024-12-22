from collections import Counter
from typing import Iterable, cast

from common.iter_utils import group_wise
from common.line_solver import LineSolver, create_summing_solution, AbstractLineByLineSolution


def parse_line(line: str) -> int:
    return int(line.strip())


def compute_secret_number(secret: int, expansions: int = 2000) -> int:
    for _ in range(expansions):
        secret = _generate_next_secret_num(secret)
    return secret


def _generate_next_secret_num(secret: int) -> int:
    secret = _mix_prune(secret, secret << 6)
    secret = _mix_prune(secret, secret >> 5)
    secret = _mix_prune(secret, secret << 11)
    return secret


def _mix_prune(secret: int, val: int) -> int:
    return (secret ^ val) % 16777216


class MonkeyMarketSolver(AbstractLineByLineSolution[int, None]):

    def __init__(self) -> None:
        self._seq_counters: Counter[tuple[int, int, int, int]] = Counter()

    @staticmethod
    def _iter_prices(secret: int, expansions: int) -> Iterable[int]:
        for _ in range(expansions + 1):
            yield secret % 10
            secret = _generate_next_secret_num(secret)

    def process_line(self, initial_secret: int) -> None:
        prices = self._iter_prices(initial_secret, 2000)
        cur_monkey_counter: Counter[tuple[int, int, int, int]] = Counter()
        for group in group_wise(prices, 5):
            key = cast(
                tuple[int, int, int, int],
                tuple(cur - prev for prev, cur in group_wise(group, 2))
            )
            if key not in cur_monkey_counter:
                cur_monkey_counter[key] = group[-1]
        self._seq_counters.update(cur_monkey_counter)

    def result(self) -> str | int:
        return self._seq_counters.most_common(1)[0][1]


if __name__ == "__main__":
    LineSolver[int, None].construct_for_day(
        day_number=22,
        line_parser=parse_line,
        solutions=[
            create_summing_solution(compute_secret_number),
            MonkeyMarketSolver,
        ],
    ).solve_all()
