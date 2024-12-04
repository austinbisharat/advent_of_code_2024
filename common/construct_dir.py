import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
DAYS_TO_CONSTRUCT = [2]

FULL_FILE_SOLVER_TEMPLATE = """from typing import TextIO
from common.file_solver import FileSolver


LoadedDataType = ...


def load(file: TextIO) -> LoadedDataType:
    ...


def solve_pt1(data: LoadedDataType) -> int:
    ...


def solve_pt2(data: LoadedDataType) -> int:
    return 0


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number={day_num},
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
"""

LINE_SOLVER_TEMPLATE = """from common.line_solver import LineSolver, AbstractLineByLineSolution


LineDataType = ...


def parse_line(line: str) -> LineDataType:
    ...


class Part1Solution(AbstractLineByLineSolution[LineDataType]):
    def __init__(self) -> None:
        ...

    def process_line(self, line: LineDataType) -> None:
        ...

    def result(self) -> int:
        ...


class Part2Solution(AbstractLineByLineSolution[LineDataType]):
    def __init__(self) -> None:
        ...

    def process_line(self, line: LineDataType) -> None:
        ...

    def result(self) -> int:
        ...


if __name__ == "__main__":
    LineSolver[LineDataType].construct_for_day(
        day_number={day_num},
        line_parser=parse_line,
        solutions=[Part1Solution, Part2Solution]
    ).solve_all()
"""

SUMMING_TEMPLATE = """from common.line_solver import LineSolver, create_summing_solution


LineDataType = ...


def parse_line(line: str) -> LineDataType:
    ...


def part_one(data: LineDataType) -> int:
    ...


def part_two(data: LineDataType) -> int:
    ...


if __name__ == "__main__":
    LineSolver[LineDataType].construct_for_day(
        day_number={day_num},
        line_parser=parse_line,
        solutions=[
            create_summing_solution(part_one),
            create_summing_solution(part_two)
        ]
    ).solve_all()
"""


def construct_dir(
    day_number: int,
    template: str,
    option: str = 'x'
) -> None:
    directory = BASE_DIR / f"day_{day_number}"
    directory.mkdir(exist_ok=True)
    open(directory / f'input_{day_number}.txt', option).close()
    open(directory / f'sample_{day_number}.txt', option).close()
    with open(directory / f'day_{day_number}.py', option) as main_file:
        main_file.write(template.format(day_num=day_number))


if __name__ == '__main__':
    construct_dir(
        day_number=4,
        template=FULL_FILE_SOLVER_TEMPLATE,
    )
