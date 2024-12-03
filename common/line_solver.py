import abc
from numbers import Number
from typing import Generic, TypeVar, Callable, Type

LineDataType = TypeVar('LineDataType')
LineOutputType = TypeVar('LineOutputType')
ResultType = TypeVar('ResultType')


class AbstractLineByLineSolution(abc.ABC, Generic[LineDataType]):
    @abc.abstractmethod
    def __init__(self) -> None:
        ...

    @abc.abstractmethod
    def process_line(self, line: LineDataType) -> None:
        ...

    @abc.abstractmethod
    def result(self) -> str | int:
        ...


def create_summing_solution(
    line_processor: Callable[[LineDataType], Number]
) -> Type[AbstractLineByLineSolution[LineDataType]]:
    return create_line_by_line_aggregating_solution(
        line_processor=line_processor,
        reducer_func=lambda result, line_result: result + line_result,
        initial_result=0,
    )


def create_product_solution(
        line_processor: Callable[[LineDataType], Number]
) -> Type[AbstractLineByLineSolution[LineDataType]]:
    return create_line_by_line_aggregating_solution(
        line_processor=line_processor,
        reducer_func=lambda result, line_result: result * line_result,
        initial_result=1,
    )


def create_line_by_line_aggregating_solution(
    line_processor: Callable[[LineDataType], LineOutputType],
    reducer_func: Callable[[ResultType, LineOutputType], ResultType],
    initial_result: ResultType,
) -> Type[AbstractLineByLineSolution[LineDataType]]:

    class LineByLineSolution(AbstractLineByLineSolution[LineDataType]):
        def __init__(self) -> None:
            self._result = initial_result

        def process_line(self, line: LineDataType) -> None:
            self._result = reducer_func(self._result, line_processor(line))

        def result(self) -> int:
            return self._result

    return LineByLineSolution


class LineSolver(Generic[LineDataType]):
    def __init__(
        self,
        file_names: list[str],
        line_parser: Callable[[str], LineDataType],
        solutions: list[Type[AbstractLineByLineSolution[LineDataType]]],
    ) -> None:
        self._file_names = file_names
        self._line_parser = line_parser
        self.solution_classes = solutions

    @classmethod
    def construct_for_day(
        cls,
        day_number: int,
        line_parser: Callable[[str], LineDataType],
        solutions: list[Type[AbstractLineByLineSolution[LineDataType]]],
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
        solutions = [s() for s in self.solution_classes]

        try:
            with open(file_name, 'r') as f:
                for line in f:
                    self._process_line(line, solutions)
        except Exception as e:
            print(f'Failed to load or process {file_name}:  {e}')
            raise

        for i, solution in enumerate(solutions):
            try:
                result = solution.result()
                print(f'\tSolution for part {i+1}: {result}')
            except Exception as e:
                print(f'\tSolution for part {i+1} failed:  {e}')
        print(f'Done.\n')

    def _process_line(self, line: str, solutions: list[AbstractLineByLineSolution[LineDataType]]) -> None:
        try:
            line_data = self._line_parser(line)
        except Exception as e:
            print(f'Failed to parse line {line}: {e}')
            raise e

        for i, solution in enumerate(solutions):
            try:
                solution.process_line(line_data)
            except Exception as e:
                print(f'Solution {i+1} failed to process line {line}:  {e}')
