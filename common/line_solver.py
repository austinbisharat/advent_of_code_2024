import abc
from numbers import Number
from typing import Generic, TypeVar, Callable

LineDataType = TypeVar('LineDataType')


class AbstractLineByLineSolution(abc.ABC, Generic[LineDataType]):

    @abc.abstractmethod
    def initialize(self) -> None:
        ...

    @abc.abstractmethod
    def process_line(self, line: LineDataType) -> None:
        ...

    @abc.abstractmethod
    def result(self) -> str | int:
        ...


class SummingLineByLineSolution(AbstractLineByLineSolution[LineDataType]):
    def __init__(self, process_line: Callable[[LineDataType], Number]) -> None:
        self._process_line = process_line
        self._result = 0

    def initialize(self) -> None:
        self._result = 0

    def process_line(self, line: LineDataType) -> None:
        self._result += self._process_line(line)

    def result(self) -> int:
        return self._result


class LineSolver(Generic[LineDataType]):
    def __init__(
        self,
        file_names: list[str],
        line_parser: Callable[[str], LineDataType],
        solutions: list[AbstractLineByLineSolution[LineDataType]],
    ) -> None:
        self._file_names = file_names
        self._line_parser = line_parser
        self._solutions = solutions

    @classmethod
    def construct_for_day(
        cls,
        day_number: int,
        line_parser: Callable[[str], LineDataType],
        solutions: list[AbstractLineByLineSolution[LineDataType]],
    ) -> 'LineSolver[LineDataType]':
        return cls(
            file_names=[f'sample_{day_number}.txt', f'input_{day_number}.txt'],
            line_parser=line_parser,
            solutions=solutions,
        )

    def solve_all(self) -> None:
        for file_name in self._file_names:
            self.solve_file(file_name)

    def solve_file(self, file_name: str) -> None:
        print(f'Solving {file_name}:')
        for solution in self._solutions:
            solution.initialize()

        try:
            with open(file_name, 'r') as f:
                for line in f:
                    self._process_line(line)
        except Exception as e:
            print(f'Failed to load or process {file_name}:  {e}')
            raise

        for i, solution in enumerate(self._solutions):
            try:
                result = solution.result()
                print(f'\tSolution for part {i+1}: {result}')
            except Exception as e:
                print(f'\tSolution for part {i+1} failed:  {e}')
        print(f'Done.\n')

    def _process_line(self, line: str) -> None:
        try:
            line_data = self._line_parser(line)
        except Exception as e:
            print(f'Failed to parse line {line}: {e}')
            raise e

        for i, solution in enumerate(self._solutions):
            try:
                solution.process_line(line_data)
            except Exception as e:
                print(f'Solution {i+1} failed to process line {line}:  {e}')
