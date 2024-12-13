import dataclasses
import re
from collections import deque
from typing import TextIO, Sequence, Iterable, cast

from common.file_solver import FileSolver

_CLAW_MACHINE_INFO_MATCHER = re.compile(
    r"^[\w\s]*: X\+(\d+), Y\+(\d+)\n[\w\s]*: X\+(\d+), Y\+(\d+)\n^[\w\s]*: X=(\d+), Y=(\d+)",
    flags=re.MULTILINE,
)


def _determinant(left: tuple[int, int], right: tuple[int, int]) -> int:
    l, r = (a * b for a, b in zip(left, reversed(right)))
    return l - r


@dataclasses.dataclass(frozen=True, eq=True)
class ClawMachineInfo:
    button_a: tuple[int, int]
    button_b: tuple[int, int]
    prize_location: tuple[int, int]

    def min_tokens_to_score(self) -> int:
        denominator = _determinant(self.button_a, self.button_b)
        if denominator == 0:
            raise NotImplementedError('Need to handle colinear/zeros cases')

        unscaled_a_count = (self.prize_location[0] * self.button_b[1] - self.prize_location[1] * self.button_b[0])
        unscaled_b_count = (self.button_a[0] * self.prize_location[1] - self.button_a[1] * self.prize_location[0])
        if unscaled_a_count % denominator != 0 or unscaled_b_count % denominator != 0:
            return 0
        return 3 * unscaled_a_count // denominator + 1 * unscaled_b_count // denominator


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


def min_score_all_prizes(data: Iterable[ClawMachineInfo]) -> int:
    results = (
        claw.min_tokens_to_score()
        for claw in data
    )
    return sum(int(r) for r in results)


def min_score_scaled_prizes(data: Iterable[ClawMachineInfo]) -> int:
    return min_score_all_prizes(
        dataclasses.replace(
            claw,
            prize_location=cast(tuple[int, int], tuple(dim + 10_000_000_000_000 for dim in claw.prize_location)),
        )
        for claw in data
    )


if __name__ == "__main__":
    FileSolver[Sequence[ClawMachineInfo]].construct_for_day(
        day_number=13,
        loader=load,
        solutions=[min_score_all_prizes, min_score_scaled_prizes]
    ).solve_all()
