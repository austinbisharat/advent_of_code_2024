import abc
import collections
import dataclasses
import heapq
import itertools
from typing import TypeVar, Generic, Iterable, Optional, Hashable, Sequence

NodeType = TypeVar('NodeType', bound=Hashable)


class NoSuchPathException(Exception):
    pass


@dataclasses.dataclass(order=True)
class _QueueNode(Generic[NodeType]):
    priority: float
    insertion_count: int
    cost_to_travel_to_node: float = dataclasses.field(compare=False)
    node_data: NodeType = dataclasses.field(compare=False)
    prev_node: Optional[NodeType] = dataclasses.field(compare=False)


class GraphSearcher(abc.ABC, Generic[NodeType]):
    def __init__(self):
        self._insertion_counter = itertools.count()

    def get_best_path(
        self,
        start_node: NodeType,
    ) -> tuple[Iterable[NodeType], float]:
        paths, score = self._get_best_paths(start_node, return_early=True)
        if len(paths) == 0:
            raise NoSuchPathException()
        return paths[0], score

    def get_all_best_paths(
        self,
        start_node: NodeType,
    ) -> tuple[Sequence[Iterable[NodeType]], float]:
        return self._get_best_paths(start_node, return_early=False)

    def _get_best_paths(
        self,
        start_node: NodeType,
        return_early: bool,
    ) -> tuple[Sequence[Iterable[NodeType]], float]:
        search_queue = [self._format_q_node(start_node)]
        known_scores_by_node = collections.defaultdict(lambda: float('inf'))
        known_scores_by_node[start_node] = 0
        best_path_score = float('inf')

        all_best_paths = collections.deque()
        gte = lambda x, y: x >= y
        gt = lambda x, y: x > y
        comparator = (gte if return_early else gt)
        while search_queue:
            current = heapq.heappop(search_queue)
            if self.is_terminal_node(current.node_data):
                best_path_score = min(current.cost_to_travel_to_node, best_path_score)
                all_best_paths.append(self._format_path(current))
                if return_early:
                    return all_best_paths, best_path_score

            for neighbor in self.get_neighbors(current.node_data):
                tentative_score = (
                    known_scores_by_node[current.node_data]
                    + self.edge_weight(current.node_data, neighbor)
                )
                if comparator(tentative_score, known_scores_by_node[neighbor]) or tentative_score > best_path_score:
                    continue
                known_scores_by_node[neighbor] = tentative_score
                heapq.heappush(search_queue, self._format_q_node(
                    node=neighbor,
                    cost_to_travel_to_node=tentative_score,
                    prev_node=current,
                ))

        return all_best_paths, best_path_score

    def _format_path(self, node: _QueueNode[NodeType]) -> Iterable[NodeType]:
        path = collections.deque()
        while node is not None:
            path.appendleft(node.node_data)
            node = node.prev_node
        return path

    def _format_q_node(
        self,
        node: NodeType,
        cost_to_travel_to_node: float = 0.0,
        prev_node: Optional[_QueueNode[[NodeType]]] = None,
    ) -> _QueueNode[NodeType]:
        return _QueueNode(
            priority=cost_to_travel_to_node + self.heuristic(node),
            insertion_count=next(self._insertion_counter),
            cost_to_travel_to_node=cost_to_travel_to_node,
            node_data=node,
            prev_node=prev_node,
        )

    @abc.abstractmethod
    def get_neighbors(self, node: NodeType) -> Iterable[NodeType]:
        ...

    @abc.abstractmethod
    def edge_weight(self, orig: NodeType, neighbor: NodeType) -> float:
        return 1

    @abc.abstractmethod
    def is_terminal_node(self, node: NodeType) -> bool:
        ...

    # Override this to use A* instead of dijkstra's
    def heuristic(self, orig: NodeType) -> float:
        return 0.0
