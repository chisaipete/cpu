from instructions import instruction
import logging
isa_log = logging.getLogger('isa')

class isa():
    def __init__(self, name):
        self.name = name
        self.word_width = 0
        self.opcode_map = {}
        self.opcode_format = {}
        self.assembler_directives = {}
