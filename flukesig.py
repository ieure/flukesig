#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2013 Ian Eure.
# Author: Ian Eure
#

"""Fluke 9010a checksum tool."""

import sys
from operator import xor, itemgetter
from array import array
from optparse import OptionParser


def readbytes(inp):
    """Return an array of bytes read from inp."""
    buf = array("B")
    try:
        while True:
            buf.fromfile(inp, 1024)
    except EOFError:
        pass
    return buf


def shiftbits(x):
    return (x >> 6) ^ (x >> 8) ^ (x >> 11) ^ (x >> 15)


def checksum(inp):
    """Return the checksum of the input."""

    buf = [0] * 16               # Buffer of checksummed bytes
    offsets = [6, 8, 11, 15, 0]  # Pointers into buf
    for byte in readbytes(inp):
        # This XORs the current byte of the file with the bytes of
        # `buf' pointed to by positions 0-3 in `offsets'. The result
        # is stored into `buf', in the position indicated by the last
        # element of `offsets'.
        buf[offsets[-1]] = reduce(xor, itemgetter(*offsets[:-1])(buf), byte)

        # Decrement offsets
        # The offsets array contains a list of pointers which sweep
        # downwards through the range of `buf'. Each pointer in
        # `offsets' is decremented after the XOR operation, resetting
        # it back to the last element of `buf' when it reaches the
        # lower bound.
        offsets = [(x - 1) % len(buf) for x in offsets]

    # Final checksum calculation. I don't understand all of this code yet.
    sig = 0
    for byte in buf:
        for _ in xrange(8):
            sig = (sig << 1) | ((byte ^ shiftbits(sig)) & 1)
            byte = byte >> 1

    # Truncate sig to the 16 least significant bits
    return sig % 2 ** 16


def get_parser():
    """Return an OptionParser."""
    return OptionParser("""Usage: %prog file1 file2 ... fileN

    Calculates the checksum of specified files using the Fluke 9010a
    algorithm.""")


def main(argv):
    parser = get_parser()
    (_, args) = parser.parse_args(argv)
    for inpf in args:
        with open(inpf, "rb") as inp:
            cksum = checksum(inp)
            print "%s %04x" % (inpf, cksum)


if __name__ == '__main__':
    main(sys.argv[1:])
