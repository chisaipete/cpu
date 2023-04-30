#!/usr/bin/env python
import logging
instruction_log = logging.getLogger('instruction')


class Instruction:
    def __init__(self, opcode, destination=(), source=(), immediate=()):
        # opcode = n-bit vector
        # destination = tuple (number, names)
        # source = tuple (number, names)
        # immediate = tuple (number, names)
        self.opcode = opcode
        self.destination = destination
        self.source = source
        self.immediate = immediate
