from common.line_solver import LineSolver, create_summing_solution


LineDataType = ...


def parse_line(line: str) -> LineDataType:
    ...


def part_one(data: LineDataType) -> int:
    ...


def part_two(data: LineDataType) -> int:
    ...


if __name__ == "__main__":
    LineSolver[LineDataType].construct_for_day(
        day_number=3,
        line_parser=parse_line,
        solutions=[
            create_summing_solution(part_one),
            create_summing_solution(part_two)
        ]
    ).solve_all()
