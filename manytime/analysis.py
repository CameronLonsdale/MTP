"""
Analysis Module
"""

import string
import collections

from typing import Iterable, List, Optional


def is_space(char: int) -> bool:
    """
    An XOR'ed character will be a space (or any punctuation character)
    if the resulting XOR of a ^ b is either 0x00, or an ascii letter
    """
    return char == 0x00 or chr(char) in string.ascii_letters


def xor(a: bytearray, b: bytearray) -> List[int]:
    """XOR two bytearrays, truncates to shortest array"""
    return [c ^ d for c, d in zip(a, b)]


def track_spaces(text: List[int]) -> collections.Counter:
    """Keep track of the spaces in text"""
    counter: collections.Counter = collections.Counter()
    for index, char in enumerate(text):
        if is_space(char):
            counter[index] += 1

    return counter


def recover_partial_key(ciphertexts: Iterable[bytearray]) -> List[Optional[int]]:
    """Using a set of ciphertexts, analyse for the space character in plaintext to recover part of the key"""
    shortest_text = min(len(text) for text in ciphertexts)
    key: List[Optional[int]] = [None for _ in range(shortest_text)]

    for main_index, main_ciphertext in enumerate(ciphertexts):
        main_counter: collections.Counter = collections.Counter()

        for secondary_index, secondary_ciphertext in enumerate(ciphertexts):
            # Dont need to XOR itself
            if main_index != secondary_index:
                # Although we know it is a space we don't know which ciphertext it came from
                main_counter.update(track_spaces(xor(main_ciphertext, secondary_ciphertext)))

        # Now we have tracked all the possible spaces we have seen, anchored to the index of the main ciphertext where we saw it
        # Therefore, if we have seen a space len(ciphertexts) - 1 times in a certain position, we know that because it was present
        # when XORd with each ciphertext, that it must have come from the main_ciphertext. Meaning, that position is a space in the main_plaintext
        for index, count in main_counter.items():
            if count == len(ciphertexts) - 1:
                key[index] = ord(' ') ^ main_ciphertext[index]

    return key


def recover_key(ciphertexts: Iterable[bytearray]) -> List[Optional[int]]:
    """
    Recovering the key consists of iteratively recovering partial keys,
    and then stitching those together.

    Each iteration we exclude the shortest ciphertext, then anaylyse
    the remaining texts using the slice after the last removed text.
    This way we get data on every part of the key, only that the
    further along the key we recover, the less ciphertexts we have to analyse.
    """
    sorted_ciphertexts = sorted(ciphertexts, key=len)
    key: List[Optional[int]] = []

    # We need a minium of two ciphertexts to compare
    while len(sorted_ciphertexts) > 1:
        key += recover_partial_key(sorted_ciphertexts)

        # Remove first element from list as we want to compare
        # all strings longer than that one
        string_length = len(sorted_ciphertexts[0])
        sorted_ciphertexts = sorted_ciphertexts[1:]
        for i in range(len(sorted_ciphertexts)):
            # Truncate all strings so we don't recalculate already known key bits
            sorted_ciphertexts[i] = sorted_ciphertexts[i][string_length:]

    return key
