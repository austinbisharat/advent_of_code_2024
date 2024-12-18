import itertools
from collections import deque
from typing import Sequence, Callable

RegisterStateDataType = tuple[int, int, int]
ProgramDataType = Sequence[int]


class InvalidProgramStateException(Exception):
    pass


class ChronospatialComputer:
    def __init__(self, register_state: RegisterStateDataType) -> None:
        self._registers = list(register_state)
        self._operations: Sequence[Callable[[int], None]] = [
            self._adv,
            self._bxl,
            self._bst,
            self._jnz,
            self._bxc,
            self._out,
            self._bdv,
            self._cdv,
        ]
        self._results = deque()
        self._instruction_pointer = 0

    def set_register_state(self, register_state: RegisterStateDataType) -> None:
        self._registers = list(register_state)

    def run_program(self, program: ProgramDataType) -> Sequence[int]:
        self._results = deque()
        self._instruction_pointer = 0
        while self._instruction_pointer < len(program):
            op_code, operand = program[self._instruction_pointer], program[self._instruction_pointer + 1]
            self._operations[op_code](operand)

        return self._results

    def _get_combo_value(self, operand: int) -> int:
        if operand <= 3:
            return operand
        elif operand <= 6:
            return self._registers[operand - 4]
        else:
            raise InvalidProgramStateException('Should never happen')

    def _dv(self, operand: int, register: int) -> None:
        combo_value = self._get_combo_value(operand)
        self._registers[register] = self._registers[0] // (1 << combo_value)
        self._instruction_pointer += 2

    def _adv(self, operand: int) -> None:
        self._dv(operand, 0)

    def _bdv(self, operand: int) -> None:
        self._dv(operand, 1)

    def _cdv(self, operand: int) -> None:
        self._dv(operand, 2)

    def _bxl(self, operand: int) -> None:
        self._registers[1] ^= operand
        self._instruction_pointer += 2

    def _bst(self, operand: int) -> None:
        self._registers[1] = self._get_combo_value(operand) % 8
        self._instruction_pointer += 2

    def _jnz(self, operand: int) -> None:
        if self._registers[0] == 0:
            self._instruction_pointer += 2
        else:
            self._instruction_pointer = operand

    def _bxc(self, operand: int) -> None:
        self._registers[1] ^= self._registers[2]
        self._instruction_pointer += 2

    def _out(self, operand: int) -> None:
        self._results.append(self._get_combo_value(operand) % 8)
        self._instruction_pointer += 2

    def pretty_format_program(self, program: ProgramDataType) -> str:
        return '\n'.join(
            f'{self._operations[opcode].__name__}: {operand}'
            for opcode, operand in itertools.batched(program, 2)
        )
