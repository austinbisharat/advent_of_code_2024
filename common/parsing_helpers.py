from typing import TextIO, Iterable
import re


def load_lines(file: TextIO) -> Iterable[str]:
    for line in file:
        yield line.strip()


def load_numeric_grid(file: TextIO) -> list[list[int]]:
    return [
        split_nums(line)
        for line in load_lines(file)
    ]


def split_nums(line: str) -> list[int]:
    return [int(value) for value in re.split(r'\s+', line.strip())]
