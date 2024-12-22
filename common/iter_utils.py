from collections import deque
from typing import TypeVar, Iterable

T = TypeVar('T')


def group_wise(iterable: Iterable[T], group_length: int) -> Iterable[tuple[T]]:
    group = deque((), group_length)
    for element in iterable:
        group.append(element)
        if len(group) != group_length:
            continue
        yield tuple(group)
