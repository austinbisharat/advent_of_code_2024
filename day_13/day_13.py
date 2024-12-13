import dataclasses
import math
import re
from collections import deque
from typing import TextIO, Sequence

from common.file_solver import FileSolver
from common.grid import subtract_relative_point

_CLAW_MACHINE_INFO_MATCHER = re.compile(
    r"^[\w\s]*: X\+(\d+), Y\+(\d+)\n[\w\s]*: X\+(\d+), Y\+(\d+)\n^[\w\s]*: X=(\d+), Y=(\d+)",
    flags=re.MULTILINE,
)


@dataclasses.dataclass(frozen=True, eq=True)
class ClawMachineInfo:
    button_a: tuple[int, int]
    button_b: tuple[int, int]
    prize_location: tuple[int, int]

    def min_tokens_to_score(self) -> float:
        memo: dict[tuple[int, int], float] = {}

        def _score(prize_location: tuple[int, int]) -> float:
            if prize_location == (0, 0):
                return 0.0

            if min(prize_location) < 0:
                return float("inf")

            if prize_location in memo:
                return memo[prize_location]

            gcd = math.gcd(prize_location[0], prize_location[1])
            if gcd > 1:
                return gcd * _score(tuple(dim // gcd for dim in prize_location))

            result = min((
                _score(subtract_relative_point(prize_location, self.button_a)) + 3.0,
                _score(subtract_relative_point(prize_location, self.button_b)) + 1.0
            ))
            return memo.setdefault(prize_location, result)

        score = _score(self.prize_location)
        return score


def load(file: TextIO) -> Sequence[ClawMachineInfo]:
    results = deque()
    for match in _CLAW_MACHINE_INFO_MATCHER.findall(file.read()):
        (
            a_x, a_y,
            b_x, b_y,
            p_x, p_y
        ) = map(int, match)
        results.append(ClawMachineInfo(
            button_a=(a_x, a_y),
            button_b=(b_x, b_y),
            prize_location=(p_x, p_y),
        ))
    return results


def min_score_all_prizes(data: Sequence[ClawMachineInfo]) -> int:
    results = (
        claw.min_tokens_to_score()
        for claw in data
    )
    return sum(int(r) for r in results if not math.isinf(r))


def solve_pt2(data: Sequence[ClawMachineInfo]) -> int:
    results = (
        dataclasses.replace(
            claw,
            prize_location=(claw.prize_location[0] + 10000000000000, claw.prize_location[1] + 10000000000000),
        ).min_tokens_to_score()
        for claw in data
    )
    return sum(int(r) for r in results if not math.isinf(r))


if __name__ == "__main__":
    FileSolver[Sequence[ClawMachineInfo]].construct_for_day(
        day_number=13,
        loader=load,
        solutions=[min_score_all_prizes, solve_pt2]
    ).solve_all()
