# Fluke 9010a Checksum Tool

This is a Python rewrite of Brian B’s Perl Fluke 9010a checksum tool,
which in turn was reverse engineered from QuarterArcades "calcsig,"
which was itself the product of reverse engineering the Fluke tools.

# Usage

The program accepts no options. Each argument is the name of a file to
checksum.

```
$ ./flukesig.py tempest/*
tempest/136002-125.d7 c706
tempest/136002-133.d1 c0ff
tempest/136002-134.f1 e47d
tempest/136002-136.lm1 e810
tempest/136002-138.np3 1720
tempest/136002-235.j1 fc98
tempest/136002-237.p1 5752
tempest/136002.126 f5cf
tempest/136002.127 76b6
tempest/136002.128 3da2
tempest/136002.129 c0b1
tempest/136002.130 b5ae
tempest/136002.131 5a82
tempest/136002.132 b112
```

# Fluke 9010a?

The Fluke 9010a is an old tool for troubleshooting microprocessor
based systems. It can calculate the checksum of parts of the address
space, for example, to verify ROM contents.
