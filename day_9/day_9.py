import collections
from typing import TextIO, Iterable, Deque

from common.file_solver import FileSolver

_MAX_FILE_SIZE = 9
_MIN_FILE_ID_NONCE = -1


def load(file: TextIO) -> str:
    return file.read().strip()


def _naive_collapse_file_system(file_data: str) -> Iterable[int]:
    if len(file_data) % 2 == 2:
        file_data = file_data[:-1]

    if not file_data:
        return 0

    cur_idx, last_idx = 0, len(file_data) - 1
    remaining_file_size_at_cur_idx = int(file_data[cur_idx])
    remaining_gap_size_at_cur_idx = int(file_data[cur_idx + 1])
    remaining_file_size_at_last_file = int(file_data[last_idx])

    while cur_idx < last_idx:
        if cur_idx % 2 == 0 and remaining_file_size_at_cur_idx:
            remaining_file_size_at_cur_idx -= 1
            yield cur_idx // 2
        elif cur_idx % 2 == 0:
            cur_idx += 1
            remaining_gap_size_at_cur_idx = int(file_data[cur_idx])
        elif cur_idx % 2 == 1 and remaining_gap_size_at_cur_idx and remaining_file_size_at_last_file:
            yield last_idx // 2
            remaining_gap_size_at_cur_idx -= 1
            remaining_file_size_at_last_file -= 1
        elif not remaining_gap_size_at_cur_idx:
            cur_idx += 1
            remaining_file_size_at_cur_idx = int(file_data[cur_idx])
        else:
            last_idx -= 2
            remaining_file_size_at_last_file = int(file_data[last_idx])

    for _ in range(remaining_file_size_at_last_file):
        yield last_idx // 2


def solve_pt1(data: str) -> int:
    return sum(
        digit * index
        for index, digit in enumerate(_naive_collapse_file_system(data))
    )


def _collapse_file_system_non_fragmented(file_data: str) -> Iterable[int]:
    if len(file_data) % 2 == 2:
        file_data = file_data[:-1]

    if not file_data:
        yield 0
        return

    file_size_to_desc_file_ids: list[Deque[tuple[int, int]]] = [collections.deque() for _ in range(10)]
    for i, val in enumerate(file_data[::2]):
        file_size = int(val)
        file_size_to_desc_file_ids[file_size].appendleft((i, file_size))

    moved_file_ids = set()
    for i, val in enumerate(file_data):
        if i % 2 == 0:
            file_size = int(val)
            file_id = i // 2
            already_moved = file_id in moved_file_ids
            for _ in range(file_size):
                yield file_id if not already_moved else 0
            if not already_moved:
                file_size_to_desc_file_ids[file_size].pop()
        else:
            gap_size = int(val)
            while gap_size > 0:
                try:
                    potential_files = (d[0] for d in file_size_to_desc_file_ids[1:gap_size + 1] if d)
                    file_id, file_size = max(potential_files, key=lambda f: f[0])
                except ValueError:
                    break

                file_size_to_desc_file_ids[file_size].popleft()
                for _ in range(file_size):
                    yield file_id
                moved_file_ids.add(file_id)
                gap_size -= file_size
            for _ in range(gap_size):
                yield 0


def solve_pt2(data: str) -> int:
    return sum(
        digit * index
        for index, digit in enumerate(_collapse_file_system_non_fragmented(data))
    )


if __name__ == "__main__":
    FileSolver[str].construct_for_day(
        day_number=9,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
