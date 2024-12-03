from typing import Generic, TypeVar, Callable, TextIO

T = TypeVar('T')


class FileSolver(Generic[T]):
    def __init__(
            self,
            file_names: list[str],
            loader: Callable[[TextIO], T],
            solutions: list[Callable[[T], str | int]],
    ) -> None:
        self._file_names = file_names
        self._loader = loader
        self._solutions = solutions

    @classmethod
    def construct_for_day(
        cls,
        day_number: int,
        loader: Callable[[TextIO], T],
        solutions: list[Callable[[T], str | int]],
    ) -> 'FileSolver[T]':
        return cls(
            file_names=[f'sample_{day_number}.txt', f'input_{day_number}.txt'],
            loader=loader,
            solutions=solutions,
        )

    def solve_all(self) -> None:
        for file_name in self._file_names:
            self.solve_file(file_name)

    def solve_file(self, file_name: str) -> None:
        print(f'Solving {file_name}:')
        try:
            with open(file_name, 'r') as f:
                data = self._loader(f)
        except Exception as e:
            print(f'Failed to load {file_name}:  {e}')
            raise

        for i, solution in enumerate(self._solutions):
            try:
                result = solution(data)
                print(f'\tSolution for part {i+1}: {result}')
            except Exception as e:
                print(f'\tSolution for part {i+1} failed:  {e}')
        print(f'Done.\n')
