import dataclasses
import itertools
import unittest

from day_2.day_2 import is_dampened_seq_safe


@dataclasses.dataclass(frozen=True, eq=True)
class _TestCase:
    input_seq: list[int]
    expected: bool


class TestIsDampenedSeqSafe(unittest.TestCase):
    _CASES = [
        *(
            _TestCase(
                input_seq=list(seq),
                expected=True
            )
            for seq in itertools.permutations([1, 2, 100])
        ),
        *(
            _TestCase(
                input_seq=list(seq),
                expected=False
            )
            for seq in itertools.permutations([100, 200, 300])
        )
    ]

    def test_all(self):
        for case in self._CASES:
            with self.subTest(case=case):
                self.assertEqual(is_dampened_seq_safe(case.input_seq), case.expected)

