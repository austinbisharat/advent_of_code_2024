import collections
from graphlib import TopologicalSorter
from typing import TextIO

from common.file_solver import FileSolver


class PageRuleGraph:
    def __init__(self):
        self._forward_rules: dict[int, set[int]] = collections.defaultdict(set)
        self._backward_rules: dict[int, set[int]] = collections.defaultdict(set)

    def add_rule(self, left: int, right: int) -> None:
        self._forward_rules[left].add(right)
        self._backward_rules[right].add(left)

    def is_valid_seq(self, sequence: list[int]) -> int:
        invalid_future_values: set[int] = set()
        for val in sequence:
            if val in invalid_future_values:
                return False
            invalid_future_values.update(self._backward_rules[val])
        return True

    def order_seq(self, sequence: list[int]) -> list[int]:
        subset = self._graph_subset(set(sequence))
        sorter = TopologicalSorter(subset._forward_rules)
        return list(sorter.static_order())

    def _graph_subset(self, relevant_values: set[int]) -> 'PageRuleGraph':
        subset = PageRuleGraph()
        for value in relevant_values:
            subset._forward_rules[value] = self._forward_rules[value].intersection(relevant_values)
            subset._backward_rules[value] = self._backward_rules[value].intersection(relevant_values)
        return subset


LoadedDataType = tuple[PageRuleGraph, list[list[int]]]


def load(file: TextIO) -> LoadedDataType:
    rules = PageRuleGraph()
    for line in file:
        if line.strip() == "":
            break

        left, right = line.strip().split("|")
        rules.add_rule(int(left), int(right))

    sequences = [
        [int(val) for val in line.strip().split(",")]
        for line in file
    ]
    return rules, sequences


def solve_pt1(data: LoadedDataType) -> int:
    rules, sequences = data
    return sum(
        seq[len(seq) // 2]
        for seq in sequences
        if seq and rules.is_valid_seq(seq)
    )


def solve_pt2(data: LoadedDataType) -> int:
    rules, sequences = data
    reordered_sequences = (
        rules.order_seq(seq)
        for seq in sequences
        if not (seq and rules.is_valid_seq(seq))
    )
    return sum(
        seq[len(seq) // 2]
        for seq in reordered_sequences
    )


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=5,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
