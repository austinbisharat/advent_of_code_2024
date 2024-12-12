import dataclasses

from common.file_solver import FileSolver
from common.grid import *

T = TypeVar('T')


def triowise(iterable: Iterable[T]) -> Iterable[tuple[T, T, T]]:
    a, b, c = itertools.tee(iterable, 3)
    next(b, None)
    next(c, None)
    next(c, None)
    return zip(a, b, c)


@dataclasses.dataclass
class Region:
    perimeter: int = 0
    area: int = 0
    plots: set[PositionType] = dataclasses.field(default_factory=set)

    def cost(self) -> int:
        return self.perimeter * self.area


def solve_pt1(farm_terrain: Grid[str]) -> int:
    all_visited_plots: set[PositionType] = set()

    def compute_region(point: PositionType, region: Region) -> Region:
        if point in region.plots:
            return region
        region.plots.add(point)
        all_visited_plots.add(point)
        region.area += 1
        for direction in CARDINAL_DIRS:
            neighbor_point = add_relative_point(point, direction.value)
            if not farm_terrain.is_valid_point(neighbor_point) or farm_terrain[neighbor_point] != farm_terrain[point]:
                region.perimeter += 1
            else:
                compute_region(neighbor_point, region)
        return region

    return sum((
        compute_region(point, Region()).cost()
        for point in farm_terrain.iter_points()
        if point not in all_visited_plots
    ))


def solve_pt2(farm_terrain: Grid[str]) -> int:
    all_visited_plots: set[PositionType] = set()

    def compute_region(point: PositionType, region: Region) -> Region:
        if point in region.plots:
            return region
        region.plots.add(point)
        all_visited_plots.add(point)
        region.area += 1
        for neighbor_point, neighbor_value in farm_terrain.iter_neighboring_points_and_values(point):
            if neighbor_value == farm_terrain[point]:
                compute_region(neighbor_point, region)

        neighbor_are_same_region = [
            farm_terrain.is_valid_point(neighbor_point) and farm_terrain[neighbor_point] == farm_terrain[point]
            for neighbor_point in (add_relative_point(point, direction.value) for direction in Direction)
        ]
        for i in range(0, len(neighbor_are_same_region), 2):
            cur_direction = neighbor_are_same_region[i]
            diagonal_dir = neighbor_are_same_region[(i + 1) % len(neighbor_are_same_region)]
            next_cardinal = neighbor_are_same_region[(i + 2) % len(neighbor_are_same_region)]
            if not cur_direction and not next_cardinal:
                # convex corner
                region.perimeter += 1
            elif cur_direction and not diagonal_dir and next_cardinal:
                # concave corner
                region.perimeter += 1

        return region

    return sum((
        compute_region(point, Region()).cost()
        for point in farm_terrain.iter_points()
        if point not in all_visited_plots
    ))


if __name__ == "__main__":
    FileSolver[Grid[str]].construct_for_day(
        day_number=12,
        loader=load_char_grid,
        solutions=[solve_pt1, solve_pt2]
    ).solve_all()
