import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
DAYS_TO_CONSTRUCT = [2]

TEMPLATE = """from typing import TextIO
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


def construct_dir(day_number: int) -> None:
    directory = BASE_DIR / f"day_{day_number}"
    directory.mkdir(exist_ok=True)
    open(directory / f'input_{day_number}.txt', 'a').close()
    open(directory / f'sample_{day_number}.txt', 'a').close()
    with open(directory / f'day_{day_number}.py', 'w') as main_file:
        main_file.write(TEMPLATE.format(day_num=day_number))


def construct_all() -> None:
    for day in DAYS_TO_CONSTRUCT:
        construct_dir(day)


if __name__ == '__main__':
    construct_all()
