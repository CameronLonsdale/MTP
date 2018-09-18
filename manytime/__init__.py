"""
Many-time module
"""

from manytime import analysis
from manytime.interactive import interactive

from typing import Iterable


def many_time_pad_attack(ciphertexts: Iterable[bytearray]) -> None:
    """Perform a Many-time pad attack"""
    partial_key = analysis.recover_key(ciphertexts)
    interactive(ciphertexts, partial_key)
