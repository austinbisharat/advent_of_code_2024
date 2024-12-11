from typing import Generic, TypeVar, Callable, TextIO, Any

T = TypeVar('T')


class FileSolver(Generic[T]):
    def __init__(
        self,
        file_names: list[str],
        loader: Callable[[TextIO], T],
        solutions: list[Callable[[T], str | int]],
        log_func: Callable[[Any], None] = print
    ) -> None:
        self._file_names = file_names
        self._loader = loader
        self._solutions = solutions
        self._log_func = log_func

    @classmethod
    def construct_for_day(
        cls,
        day_number: int,
        loader: Callable[[TextIO], T],
        solutions: list[Callable[[T], str | int]],
        log_func: Callable[[Any], None] = print
    ) -> 'FileSolver[T]':
        return cls(
            file_names=[f'sample_{day_number}.txt', f'input_{day_number}.txt'],
            loader=loader,
            solutions=solutions,
            log_func=log_func
        )

    def solve_all(self) -> None:
        for file_name in self._file_names:
            self.solve_file(file_name)

    def solve_file(self, file_name: str) -> None:
        self._log_func(f'Solving {file_name}:')
        with open(file_name, 'r') as f:
            data = self._loader(f)

        for i, solution in enumerate(self._solutions):
            result = solution(data)
            self._log_func(f'\tSolution for part {i + 1}: {result}')
        self._log_func(f'Done.\n')
