import collections
import itertools
import math
from typing import Iterable, Deque

from common.file_solver import FileSolver
from common.grid import *


class AntennaGrid:
    def __init__(self, data: Grid[str]) -> None:
        self._grid = data
        self._antenna_locations: dict[str, Deque[PositionType]] = collections.defaultdict(collections.deque)
        for row, col in itertools.product(range(data.height), range(data.width)):
            cell = data[row, col]
            if cell == '.':
                continue
            self._antenna_locations[cell].append((row, col))

    def get_frequencies(self) -> Iterable[str]:
        return self._antenna_locations.keys()

    def get_antenna_locations(self, frequency: str) -> Sequence[PositionType]:
        return self._antenna_locations[frequency]

    def get_antinodes(self, left_antenna: PositionType, right_antenna: PositionType) -> Iterable[PositionType]:
        vec = add_point(left_antenna, scale_relative_point(right_antenna, -1))
        lower_antinode = add_point(left_antenna, vec)
        upper_antinode = add_point(right_antenna, scale_relative_point(vec, -1))
        antinodes = (lower_antinode, upper_antinode)
        return [a for a in antinodes if self._grid.is_valid_point(a)]

    def get_harmonic_antinodes(self, left_antenna: PositionType, right_antenna: PositionType) -> Iterable[PositionType]:
        rise, run = add_point(left_antenna, scale_relative_point(right_antenna, -1))
        gcd = math.gcd(rise, run)
        slope = rise // gcd, run // gcd
        cur = left_antenna
        while self._grid.is_valid_point(cur):
            yield cur
            cur = add_point(cur, scale_relative_point(slope, -1))

        cur = right_antenna
        while self._grid.is_valid_point(cur):
            yield cur
            cur = add_point(cur, slope)


LoadedDataType = AntennaGrid


def load(file: TextIO) -> LoadedDataType:
    return AntennaGrid(load_char_grid(file))


def solve_pt1(antenna_grid: LoadedDataType) -> int:
    visited: set[PositionType] = {
        position
        for freq in antenna_grid.get_frequencies()
        for left_antenna, right_antenna in itertools.combinations(antenna_grid.get_antenna_locations(freq), 2)
        for position in antenna_grid.get_antinodes(left_antenna, right_antenna)
    }
    return len(visited)


def solve_pt2(antenna_grid: LoadedDataType) -> int:
    visited: set[PositionType] = {
        position
        for freq in antenna_grid.get_frequencies()
        for left_antenna, right_antenna in itertools.combinations(antenna_grid.get_antenna_locations(freq), 2)
        for position in antenna_grid.get_harmonic_antinodes(left_antenna, right_antenna)
    }
    return len(visited)


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=8,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
