import dataclasses
import math
import re
import statistics
from collections import defaultdict
from typing import TextIO, cast

import png

from common.file_solver import FileSolver
from common.grid import add_relative_point, scale_relative_point
from common.line_solver import LineSolver, AbstractLineByLineSolution

_ROBOT_DATA_MATCHER = re.compile(r'p=(\d+),(\d+) v=(-?\d+),(-?\d+)')


class NoQuadrantException(Exception):
    pass


def _get_quadrant(point: tuple[int, int], grid_size: tuple[int, int]) -> int:
    if any(
        size % 2 == 1 and dim == size // 2
        for dim, size in zip(point, grid_size)
    ):
        raise NoQuadrantException()

    return sum(
        (dim > size // 2) << i
        for i, (dim, size) in enumerate(zip(point, grid_size))
    )


@dataclasses.dataclass
class RobotData:
    initial_position: tuple[int, int]
    velocity: tuple[int, int]

    def new_location(self, steps: int, grid_size: tuple[int, int]) -> tuple[int, int]:
        new_loc = add_relative_point(self.initial_position, scale_relative_point(self.velocity, steps))
        return cast(tuple[int, int], tuple(dim % size for dim, size in zip(new_loc, grid_size)))


FileConfigType = tuple[int, int]


def parse_file_config(file_date: TextIO) -> FileConfigType:
    width, height = file_date.readline().split(',')
    return int(width), int(height)


def parse_line(line: str) -> RobotData:
    m = _ROBOT_DATA_MATCHER.match(line)
    assert m is not None, line
    pos_x, pos_y, vel_x, vel_y = map(int, m.groups())
    return RobotData(
        initial_position=(pos_x, pos_y),
        velocity=(vel_x, vel_y),
    )


def load_file(file: TextIO) -> tuple[FileConfigType, list[RobotData]]:
    grid_size = parse_file_config(file)
    robots = [
        parse_line(line)
        for line in file
    ]
    return grid_size, robots


class Part1Solution(AbstractLineByLineSolution[RobotData, FileConfigType]):
    def __init__(self) -> None:
        self._quadrant_counts = defaultdict(int)
        self._size = (1, 1)

    def load_config(self, config: FileConfigType) -> None:
        self._size = config

    def process_line(self, r: RobotData) -> None:
        try:
            self._quadrant_counts[_get_quadrant(r.new_location(100, self._size), self._size)] += 1
        except NoQuadrantException:
            pass

    def result(self) -> int:
        return math.prod(self._quadrant_counts.values())


def construct_step_images(data: tuple[FileConfigType, list[RobotData]]) -> str:
    grid_size, robots = data
    for step in range(10_000):
        robot_locations = {
            r.new_location(step, grid_size) for r in robots
        }

        if (
            abs(statistics.stdev(r[0] for r in robot_locations) - 30) > 5
            and abs(statistics.stdev(r[1] for r in robot_locations) - 30) > 5
        ):
            img_data = [
                [
                    255 if (j, i) in robot_locations else 0
                    for j in range(grid_size[0])
                ]
                for i in range(grid_size[1])
            ]
            png.from_array(img_data, 'L').save(f'robot_images/step_{step}.png')
    return f'open robot_images/step_*.png'


if __name__ == "__main__":
    LineSolver[RobotData, FileConfigType].construct_for_day(
        day_number=14,
        line_parser=parse_line,
        file_config_parser=parse_file_config,
        solutions=[Part1Solution]
    ).solve_all()

    FileSolver[tuple[FileConfigType, list[RobotData]]].construct_for_day(
        day_number=14,
        loader=load_file,
        solutions=[construct_step_images]
    ).solve_file('input_14.txt')
