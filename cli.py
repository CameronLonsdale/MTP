#!/usr/bin/env python

import sys
import argparse

from manytime import many_time_pad_attack


parser = argparse.ArgumentParser(description='Break many time pad encryption')
parser.add_argument('file', type=str, help='file containing hexadecimal ciphertexts, delimited by new lines')
args = parser.parse_args()

with open(args.file, 'r') as f:
    ciphertexts = [line.rstrip() for line in f]

try:
    ciphertexts = list(map(bytearray.fromhex, ciphertexts))
except ValueError as error:
    sys.exit("Invalid hexadecimal: {error}")

many_time_pad_attack(ciphertexts)
