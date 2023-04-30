import argparse
import os

from common.isa import Isa
from common.assembler import Assembler
import logging
from BitVector import BitVector
import copy
hack_log = logging.getLogger('hack')


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
        self.comp_map = {  # a-value + c-value
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
        self.dest_map = {  # d-value
            'null': (BitVector(bitstring='000')),
            'M':    (BitVector(bitstring='001')),
            'D':    (BitVector(bitstring='010')),
            'MD':   (BitVector(bitstring='011')),
            'A':    (BitVector(bitstring='100')),
            'AM':   (BitVector(bitstring='101')),
            'AD':   (BitVector(bitstring='110')),
            'AMD':  (BitVector(bitstring='111')),
        }
        self.jump_map = {  # j-value
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
        self.starting_variable_allocation_address = 16


class HackAssembler(Assembler):
    def __init__(self):
        super(HackAssembler, self).__init__(Hack())
        self.symbol_table = {}
        self.load_symbol_table()
        self.line_breaks = True

    def load_symbol_table(self):
        self.symbol_table.clear()
        self.symbol_table = copy.deepcopy(self.isa.predefined_symbols)

    def parse_assembly(self):
        hack_log.info('applying the hack assembly format to input')
        self.output = []
        instruction_count = 0
        output_bitlines = []
        # print(self.symbol_table)
        input_post_first_pass = []
        for line in self.input:
            line = line.strip()
            if line:
                removed_comments = line.strip().split('//')[0].strip()
                if removed_comments:
                    if line.startswith('('):
                        label = line.split('(')[1].split(')')[0].strip()
                        # print(f"Label {label} detected at line {instruction_count + 1}")
                        if label in self.symbol_table:
                            # print("\tSymbol already defined, skipping")
                            pass
                        else:
                            self.symbol_table[label] = instruction_count
                            # print(f"\tAdding {label} to table at instruction {self.symbol_table[label]}")
                    else:
                        input_post_first_pass.append((instruction_count, removed_comments))
                        instruction_count += 1

        # print(self.symbol_table)
        # print(input_post_first_pass)

        next_available_address = self.isa.starting_variable_allocation_address

        for instruction in input_post_first_pass:
            out_bv = BitVector(size=0)
            if instruction[1].startswith('@'):
                # print(f"A instruction: {instruction[1]}")
                instruction_format = self.isa.opcode_format['a_inst']
                value = instruction[1].split('@')[1]
                if value.isdigit():
                    value = int(value)
                else:
                    if value in self.symbol_table:
                        value = self.symbol_table[value]
                    else:
                        # assign next available RAM address to this symbol
                        self.symbol_table[value] = next_available_address
                        next_available_address += 1
                        value = self.symbol_table[value]
                # print(f"A'{value}'")
                for entry in instruction_format:
                    if 'opcode' in entry[0]:
                        out_bv += self.isa.opcode_map['A'][0]
                    elif 'value' in entry[0]:
                        out_bv += BitVector(intVal=value, size=entry[1])
            else:
                # print(f"C instruction: {instruction[1]}")
                instruction_format = self.isa.opcode_format['c_inst']
                inst_eq_split = instruction[1].split('=')
                if '=' not in instruction[1]:
                    inst_semi_split = instruction[1].split(';')
                    dest = 'null'
                else:
                    inst_semi_split = inst_eq_split[1].split(';')
                    dest = inst_eq_split[0]
                comp = inst_semi_split[0]
                if len(inst_semi_split) > 1:
                    jump = inst_semi_split[1]
                else:
                    jump = 'null'
                # print(f"D'{dest}''{comp}''{jump}'")
                for entry in instruction_format:
                    if 'opcode' in entry[0]:
                        out_bv += self.isa.opcode_map['C'][0]
                    elif 'comp' in entry[0]:
                        out_bv += self.isa.comp_map[comp]
                    elif 'dest' in entry[0]:
                        out_bv += self.isa.dest_map[dest]
                    elif 'jump' in entry[0]:
                        out_bv += self.isa.jump_map[jump]

            output_bitlines.append(out_bv)

        error = False
        for idx, entry in enumerate(output_bitlines):
            if len(output_bitlines[idx]) != self.isa.word_size:
                hack_log.fatal(f"unrecognized or erroneous syntax in instruction {idx}: {output_bitlines[idx]}")
                error = True
            self.output.append(entry)
        if error:
            self.output = []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="""""", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,max_help_position=80))
    parser.add_argument('asm_file', metavar='xxx.hack', type=str, nargs='?', help='assembly file to convert')
    args = parser.parse_args()

    if args.asm_file:
        if args.asm_file == 'all':
            for file in os.listdir(os.getcwd()):
                if file.endswith('.asm'):
                    print(file)
                    asb = HackAssembler()
                    asb.input_assembly(file)
                    asb.output_binary(file.replace('.asm', '.hack'))
        else:
            asb = HackAssembler()
            asb.input_assembly(args.asm_file)
            asb.output_binary(args.asm_file.replace('.asm', '.hack'))
    else:
        asb = HackAssembler()
        asb.input_assembly('../input/sample.asm')
        asb.output_binary('../output/sample.hack')
