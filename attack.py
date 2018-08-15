#!/usr/bin/env python

import sys
import string
import collections

from interactive import Interactive

ciphertexts = sys.stdin.read().split()
try:
    ciphertexts = [bytearray.fromhex(ciphertext) for ciphertext in ciphertexts]
except ValueError as e:
    sys.exit("Invalid hexadecimal")

longest_text = max(len(text) for text in ciphertexts)
final_key = [None for _ in range(longest_text)]


def is_space(char: int):
    """An XOR'ed character will be a space (or any punctuation character)
    if the resulting XOR of a ^ b is either 0x00, or an ascii letter
    """
    return char == 0x00 or chr(char) in string.ascii_letters


def xor(a: bytearray, b: bytearray):
    """XOR two bytearrays, truncates to shortest array"""
    return [c ^ d for c, d in zip(a, b)]


def track_spaces(text: bytearray):
    """Keep track of the spaces in text"""
    counter = collections.Counter()
    for index, char in enumerate(text):
        if is_space(char):
            counter[index] += 1

    return counter


# Identify key values by assuming that punctuation characters are most likely going to be spaces
for main_index, main_ciphertext in enumerate(ciphertexts):

    main_counter = collections.Counter()
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
            final_key[index] = ord(' ') ^ main_ciphertext[index]


def partial_decrypt(key, ciphertext):
    return [chr(k ^ c) if k is not None else '*' for k, c in zip(key, ciphertext)]


# Begin decryption loop
while True:

    def on_change_hook(level, index, char):
        global final_key
        ciphertext = ciphertexts[level]
        final_key[index] = char ^ ciphertext[index]

        texts = [''.join(partial_decrypt(final_key, ciphertext)) for ciphertext in ciphertexts]
        texts[level] = ''.join(partial_decrypt(final_key, ciphertext))
        return texts

    partial_decrypts = [''.join(partial_decrypt(final_key, ciphertext)) for ciphertext in ciphertexts]
    Interactive(partial_decrypts, on_change_hook=on_change_hook).start()
