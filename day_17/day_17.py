import itertools
from typing import TextIO, cast, Sequence

from chronospatial_computer import RegisterStateDataType, ProgramDataType, ChronospatialComputer
from common.file_solver import FileSolver

LoadedDataType = tuple[RegisterStateDataType, ProgramDataType]


def load(file: TextIO) -> LoadedDataType:
    register_data = cast(tuple[int, int, int], tuple(
        int(file.readline().split(':')[1].strip())
        for _ in range(3)
    ))
    assert file.readline().strip() == ''

    _, program_data = file.readline().split(':')
    program_data = tuple(
        int(val.strip())
        for val in program_data.split(',')
    )
    return register_data, program_data


def solve_pt1(data: LoadedDataType) -> str:
    initial_register_state, program_data = data
    computer = ChronospatialComputer(initial_register_state)
    output = computer.run_program(program_data)
    return ','.join(map(str, output))


def bitmask(size: int) -> int:
    return (1 << size) - 1


_LOWER_REGISTER_BIT_MASK = bitmask(3)
_UPPER_REGISTER_BIT_MASK = bitmask(8 + 3) ^ _LOWER_REGISTER_BIT_MASK


def _run_one_cycle_forward(a: int) -> int:
    """
    Not super satisfied with this, but this is a hardcoded version of my input program, except it only
    runs one cycle and ignores the jnz at the end. Realistically, I am not sure I can think of a
    reasonable way to solve this problem generally. I think the following constraints _must_ be met for
    my approach to work:
    - There's exactly one jnz at the end of the program to an even index (in my case hardcoded to 0)
    - Each cycle does adv by some constant amount (in my case, I hardcoded 3)
    - There's exactly one output per cycle of the program, and that output only depends on the value of the A
      register at the beginning of that cycle. In my case, the out instruction outputs B, but B is set to a value
      that only depends on the lowest 10 (7 + 3) bits of A.

    My program:
    _bst: 4  # set B to A & 111
    _bxl: 1  # flip B's lowest bit
    _cdv: 5  # C = A >> B. B can be at most 7
    _bxl: 5  # B = B XOR 101. B now has A's lowest 3 bits w/ the highest bit flipped
    _bxc: 1  # B = B XOR C
    _out: B  # output register B & 111
    _adv: 3  # a >> 3
    _jnz: 0  # jump to program beginning if a > 0
    """

    b = a & _LOWER_REGISTER_BIT_MASK
    b = b ^ 1
    c = (a >> b) & _LOWER_REGISTER_BIT_MASK
    b = b ^ 5
    b = b ^ c
    return b


def _compute_lookup_table() -> Sequence[set[int]]:
    results = [set() for _ in range(8)]
    for register_a_val in range(1 << (8 + 3)):
        output = _run_one_cycle_forward(register_a_val)
        results[output].add(register_a_val)
    return results


def _combine_valid_a_state_sets(cur_valid_states: set[int], prev_valid_states: set[int]) -> set[int]:
    return {
        (prev_a << 3) | cur_a
        for prev_a, cur_a in itertools.product(prev_valid_states, cur_valid_states)
        if (
            (cur_a & _UPPER_REGISTER_BIT_MASK) ==
            (prev_a << 3) & _UPPER_REGISTER_BIT_MASK
        )
    }


def solve_pt2(data: LoadedDataType) -> int:
    _, program_data = data
    output_val_to_potential_a_vals = _compute_lookup_table()
    valid_a_states = {0}
    for i, expected_print in enumerate(reversed(program_data)):
        potential_a_vals = output_val_to_potential_a_vals[expected_print]
        valid_a_states = _combine_valid_a_state_sets(potential_a_vals, valid_a_states)

    return min(valid_a_states)


if __name__ == "__main__":
    FileSolver[LoadedDataType].construct_for_day(
        day_number=17,
        loader=load,
        solutions=[solve_pt1]
    ).solve_all()

    # Can't run pt 2 against sample input since my solution is hardcoded to my input
    FileSolver[LoadedDataType].construct_for_day(
        day_number=17,
        loader=load,
        solutions=[solve_pt2]
    ).solve_file('input_17.txt')
