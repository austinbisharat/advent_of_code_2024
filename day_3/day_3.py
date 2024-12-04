from typing import TextIO
from common.file_solver import FileSolver
import re


LoadedDataType = str


def load(file: TextIO) -> LoadedDataType:
    return file.read()


def solve_pt1(data: LoadedDataType) -> int:
    return sum((
        int(left_num) * int(right_num)
        for left_num, right_num in re.findall(r'mul\((\d{1,3}),(\d{1,3})\)', data)
    ))


def solve_pt2(data: LoadedDataType) -> int:
    result = 0
    is_enabled = True
    for start, stop, left_num, right_num in re.findall(r'(do\(\))|(don\'t\(\))|mul\((\d{1,3}),(\d{1,3})\)', data):
        if start:
            is_enabled = True
        elif stop:
            is_enabled = False

        if is_enabled and left_num and right_num:
            result += int(left_num) * int(right_num)
    return result


if __name__ == "__main__":
    FileSolver[LoadedDataType](
        file_names=['sample_3_1.txt', 'sample_3_2.txt', 'input_3.txt'],
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
