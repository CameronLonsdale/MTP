"""
Many-time module
"""

from manytime import analysis
from manytime.interactive import interactive

from typing import Iterable


def many_time_pad_attack(ciphertexts: Iterable[bytearray]) -> None:
    """
    Perform a Many-time pad attack

    First we recover as much as the key we can using automated cryptanalysis,
    then drop the user into an interactive session to complete the decryption.
    """
    partial_key = analysis.recover_key(ciphertexts)
    interactive(ciphertexts, partial_key)
