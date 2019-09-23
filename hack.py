from isa import Isa
from assembler import Assembler
import logging
from BitVector import BitVector
import copy
hack_log = logging.getLogger('hack')
from pprint import pprint


class Hack(Isa):
    def __init__(self):
        super(Hack, self).__init__('hack')
        self.word_size = 16
        self.opcode_map = {
            'A': (BitVector(bitstring='0'), 'a_inst'),
            'C': (BitVector(bitstring='111'), 'c_inst'),
        }
        self.opcode_format = {
            'a_inst': [('opcode', 1), ('value', 15)],
            'c_inst': [('opcode', 3), ('comp', 7), ('dest', 3), ('jump', 3)],
        }
        self.comp_map = { # a-value + c-value
            '0':   (BitVector(bitstring='0101010')),
            '1':   (BitVector(bitstring='0111111')),
            '-1':  (BitVector(bitstring='0111010')),
            'D':   (BitVector(bitstring='0001100')),
            'A':   (BitVector(bitstring='0110000')),
            '!D':  (BitVector(bitstring='0001101')),
            '!A':  (BitVector(bitstring='0110001')),
            '-D':  (BitVector(bitstring='0001111')),
            '-A':  (BitVector(bitstring='0110011')),
            'D+1': (BitVector(bitstring='0011111')),
            'A+1': (BitVector(bitstring='0110111')),
            'D-1': (BitVector(bitstring='0001110')),
            'A-1': (BitVector(bitstring='0110010')),
            'D+A': (BitVector(bitstring='0000010')),
            'D-A': (BitVector(bitstring='0010011')),
            'A-D': (BitVector(bitstring='0000111')),
            'D&A': (BitVector(bitstring='0000000')),
            'D|A': (BitVector(bitstring='0010101')),
            'M':   (BitVector(bitstring='1110000')),
            '!M':  (BitVector(bitstring='1110001')),
            '-M':  (BitVector(bitstring='1110011')),
            'M+1': (BitVector(bitstring='1110111')),
            'M-1': (BitVector(bitstring='1110010')),
            'D+M': (BitVector(bitstring='1000010')),
            'D-M': (BitVector(bitstring='1010011')),
            'M-D': (BitVector(bitstring='1000111')),
            'D&M': (BitVector(bitstring='1000000')),
            'D|M': (BitVector(bitstring='1010101')),
        }
        self.dest_map = { # d-value
            'null': (BitVector(bitstring='000')),
            'M':    (BitVector(bitstring='001')),
            'D':    (BitVector(bitstring='010')),
            'MD':   (BitVector(bitstring='011')),
            'A':    (BitVector(bitstring='100')),
            'AM':   (BitVector(bitstring='101')),
            'AD':   (BitVector(bitstring='110')),
            'AMD':  (BitVector(bitstring='111')),
        }
        self.jump_map = { # j-value
            'null': (BitVector(bitstring='000')),
            'JGT':  (BitVector(bitstring='001')),
            'JEQ':  (BitVector(bitstring='010')),
            'JGE':  (BitVector(bitstring='011')),
            'JLT':  (BitVector(bitstring='100')),
            'JNE':  (BitVector(bitstring='101')),
            'JLE':  (BitVector(bitstring='110')),
            'JMP':  (BitVector(bitstring='111')),
        }
        self.predefined_symbols = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576,
        }


class HackAssembler(Assembler):
    def __init__(self):
        super(HackAssembler, self).__init__(Hack())
        self.symbol_table = {}
        self.load_symbol_table()

    def load_symbol_table(self):
        self.symbol_table.clear()
        self.symbol_table = copy.deepcopy(self.isa.predefined_symbols)

    def parse_assembly(self):
        hack_log.info('applying the hack assembly format to input')
        self.output = []
        symbol_table = {}
        instruction_count = 0
        output_bitlines = []
        for line in self.input:
            line = line.strip()
            if line:
                removed_comments = line.strip().split('//')[0].strip()
                if removed_comments:
                    if line.startswith('@'):
                        instruction_count += 1
                    elif line.startswith('('):

                    print(line)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asb = HackAssembler()

    asb.input_assembly('sample.hasm')
    asb.output_binary('sample.hack')
