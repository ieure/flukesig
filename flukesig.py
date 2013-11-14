#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# © 2013 Ian Eure.
# Author: Ian Eure
#

"""Fluke 9010a checksum tool."""

import sys
import zipfile
from operator import xor, itemgetter
from itertools import chain
from contextlib import closing
from array import array
from optparse import OptionParser
from os.path import basename

BLOCK_SIZE = 1024               # Read this many bytes at a time


def readbytes(inp):
    """Return an array of bytes read from inp."""
    buf = array("B")
    done = False
    while not done:
        temp = inp.read(BLOCK_SIZE)
        buf.fromstring(temp)
        done = len(temp) < BLOCK_SIZE
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
    parser = OptionParser("""Usage: %prog file1 file2 ... fileN

    Calculates the checksum of specified files using the Fluke 9010a
    algorithm.""")

    parser.add_option("--no-unzip", action="store_false", default=True,
                      help="Disable checksumming files inside ZIP archives.")
    parser.add_option("-s", "--short",
                      action="store_true", default=False,
                      help="Omit directory names from output.")

    return parser


def gen_zip_fds(inpf, fd):
    """Return a generator of (filename, fd).

       The generator returns the files inside the ZIP archive.
    """
    with closing(zipfile.ZipFile(fd)) as zfd:
        for zfn in zfd.namelist():
            with closing(zfd.open(zfn)) as fd:
                yield ("%s:%s" % (inpf, zfn), fd)


def gen_fds(args, unzip=True):
    """Return a generator of tuples of (filename, fd) for the inputs.

       If unzip is set to False, ZIP files will be checksummed, rather
       than the files inside them."""
    for inpf in args:
        with open(inpf, "rb") as fd:
            if unzip and zipfile.is_zipfile(inpf):
                yield gen_zip_fds(inpf, fd)
            else:
                yield ((inpf, fd),)


def main(argv):
    parser = get_parser()
    (opts, args) = parser.parse_args(argv)
    for (inpf, fd) in chain.from_iterable(gen_fds(args, opts.no_unzip)):
        print "%s %04x" % (basename(inpf) if opts.short else inpf,
                           checksum(fd))


if __name__ == '__main__':
    main(sys.argv[1:])
