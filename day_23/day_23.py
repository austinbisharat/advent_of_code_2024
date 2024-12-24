import collections
from typing import TextIO, Deque

from common.file_solver import FileSolver

LanNetworkGraphType = dict[str, set[str]]


def load(file: TextIO) -> LanNetworkGraphType:
    g = collections.defaultdict(set)
    for line in file:
        left_comp, right_comp = line.strip().split('-')
        g[left_comp].add(right_comp)
        g[right_comp].add(left_comp)
    return g


def solve_pt1(lan_graph: LanNetworkGraphType) -> int:
    def uniq_cycles_of_exact_length(
        path: Deque[str],
        cycle_len: int,
    ) -> set[tuple[str, ...]]:
        if len(path) == cycle_len and path[0] in lan_graph[path[-1]]:
            return {tuple(sorted(path))}
        elif len(path) == cycle_len:
            return set()
        else:
            relevant_neighbors = (
                n
                for n in lan_graph[path[-1]]
                if n not in path
            )
            result = set()
            for n in relevant_neighbors:
                path.append(n)
                result.update(uniq_cycles_of_exact_length(path, cycle_len))
                path.pop()
            return result

    cycles = set()
    for comp_id in lan_graph:
        cycles.update(uniq_cycles_of_exact_length(
            path=collections.deque((comp_id,)),
            cycle_len=3,
        ))

    def _cycle_predicate(cycle: tuple[str, ...]) -> bool:
        return any(cid.startswith('t') for cid in cycle)

    return sum(
        1
        for cycle in cycles
        if _cycle_predicate(cycle)
    )


def solve_pt2(lan_graph: LanNetworkGraphType) -> str:
    visited = set()

    def get_largest_complete_subgraph_of_min_size(
        clique_so_far: set[str],
        potential_nodes: set[str],
    ) -> set[str]:
        key = tuple(sorted(clique_so_far))
        if tuple(key) in visited:
            return set()
        visited.add(key)

        if not potential_nodes:
            return clique_so_far.copy()

        best_subgraph = set()
        for node in potential_nodes:

            neighbors = lan_graph[node]
            if not neighbors.issuperset(clique_so_far):
                continue
            clique_so_far.add(node)
            r = get_largest_complete_subgraph_of_min_size(
                clique_so_far,
                neighbors.difference(clique_so_far).intersection(potential_nodes),
            )
            clique_so_far.remove(node)

            if len(r) > len(best_subgraph):
                best_subgraph = r

        return best_subgraph

    best_subgraph = get_largest_complete_subgraph_of_min_size(set(), set(lan_graph.keys()))
    return ','.join(sorted(best_subgraph))


if __name__ == "__main__":
    FileSolver[LanNetworkGraphType].construct_for_day(
        day_number=23,
        loader=load,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
