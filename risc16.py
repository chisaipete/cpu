from isa import Isa
from assembler import Assembler
import logging
from BitVector import BitVector
risc16_log = logging.getLogger('risc16')
from pprint import pprint


class Risc16(Isa):
    def __init__(self):
        super(Risc16, self).__init__('risc16')
        self.word_size = 16
        self.opcode_map = { # code, format
            'add':  (BitVector(bitstring='000'), 'rrr'),
            'addi': (BitVector(bitstring='001'), 'rri'),
            'nand': (BitVector(bitstring='010'), 'rrr'),
            'lui':  (BitVector(bitstring='011'), 'ri'),
            'sw':   (BitVector(bitstring='100'), 'rri'),
            'lw':   (BitVector(bitstring='101'), 'rri'),
            'beq':  (BitVector(bitstring='110'), 'rri'),
            'jalr': (BitVector(bitstring='111'), 'rri'),
        }

        self.opcode_format = {
            'rrr' : [('opcode', 3), ('regA', 3), ('regB', 3), ('0', 4), ('regC', 3)],
            'rri' : [('opcode', 3), ('regA', 3), ('regB', 3), ('immsign', 7)],
            'ri'  : [('opcode', 3), ('regA', 3), ('imm', 10)],
        }

        self.assembler_directives = { # check documentation
            'nop'   : ('add',[0,0,0]),
            'halt'  : ('jalr',[0,0],1),
            'lli'   : (),
            'movi'  : (),
            '.fill' : (),
            '.space': (),
        }


class Risc16Assembler(Assembler):
    def __init__(self):
        super(Risc16Assembler, self).__init__(Risc16())
        # self.line_breaks = True

    def parse_assembly(self):
        risc16_log.info('applying the risc16 assembly format to input')
        self.output = []
        labels = {}
        instruction_count = 0
        output_bitlines = []
        for line in self.input:
            # print(line)   
            label = ''
            opcode = ''
            fields = []
            register_fields = []
            immediate = ''
            # comments, all after # is ignored
            removed_comments = line.strip().split('#')[0].strip()
            # print(removed_comments)
            if removed_comments:
                # Format:
                #   label:<whitespace>opcode<whitespace>field0, field1, field2<whitespace># comments
                # label = letters and numbers
                # optional whitespace
                post_label = removed_comments
                if ':' in removed_comments:
                    label = removed_comments.split(':', 1)[0].strip()
                    post_label = removed_comments.split(':', 1)[1].strip()
                    labels[label] = instruction_count
                # print(">", label, "<||>", post_label, "<", sep='')
                if post_label:
                    # opcode = letters (mnemonics)
                    # needed whitespace
                    pl_split = post_label.split(maxsplit=1)
                    opcode = pl_split[0].strip().lower()
                    remainder = ''
                    if len(pl_split) > 1:
                        remainder = pl_split[1].strip()
                    if remainder:
                        # fields separated by comma, whitespace, or both
                        if ',' in remainder:
                            fields = [r.strip() for r in remainder.split(',')]
                        else:
                            fields = remainder.split()
                        if fields:
                            # register-value fields = decimal numbers, can be preceded with 'r' r1|1
                            # immediate-value fields = decimal/octal/hexadecimal, octal="0..."  hex="0x..."
                            opcode_entry = self.isa.opcode_map.get(opcode, None)
                            if opcode_entry:
                                instruction_format = self.isa.opcode_format.get(opcode_entry[1], None)
                                for entry in instruction_format:
                                    if 'opcode' in entry[0]:
                                        continue
                                    elif 'reg' in entry[0]:
                                        register_fields.append(fields.pop(0).replace('r', ''))
                                    elif 'imm' in entry[0]:
                                        immediate = fields.pop(0)
                                    elif '0' in entry[0]:
                                        continue
            if opcode:
                # print(instruction_count, label, opcode, fields, register_fields, immediate)
                output_bitlines.append([instruction_count, label, opcode, fields, register_fields, immediate])
                instruction_count += 1
                if opcode == 'movi':
                    # movi is a directive which inserts two instructions
                    instruction_count += 1
                elif opcode == '.space':
                    # this inserts n 16 byte words worth of 0 into the stream, we should probably
                    # increment by this integer (-1)
                    instruction_count += int(fields[0]) - 1
                    # TODO: be able to use symbolic references here

        # pprint(labels)
        idx = 0
        for i in output_bitlines:
            space = 1
            # print(output_bitlines[idx])
            # label substitution (immediate)
            if i[5] in labels:
                i[5] = labels[i[5]]
            # directive handling
            if i[2] in self.isa.assembler_directives:
                directive = i[2]
                if directive == '.fill':
                    imm = i[3][0]
                    if imm[0] == '-':
                        # manually handle negative numbers as two's complement (invert and add 1)
                        imm = imm[1:]
                        imm_bv = ~(BitVector(intVal=int(imm), size=self.isa.word_size))
                        imm_bv = BitVector(intVal=int(imm_bv)+1, size=self.isa.word_size)
                    elif imm.isalpha():
                        # label substitution
                        imm_bv = BitVector(intVal=int(labels[imm]), size=self.isa.word_size)
                    else:
                        imm_bv = BitVector(intVal=int(imm), size=self.isa.word_size)
                    output_bitlines[idx] = imm_bv
                elif directive == '.space':
                    imm = i[3][0]
                    if imm.isalpha():
                        # label substitution
                        for c in range(idx, int(labels[imm])+idx):
                            output_bitlines[c] = BitVector(size=self.isa.word_size)
                        space = int(labels[imm])
                    else:
                        for c in range(idx, int(imm)+idx):
                            output_bitlines[c] = BitVector(size=self.isa.word_size)
                        space = int(imm)
                elif directive in ['halt', 'nop']:
                    output_bitlines[idx][2] = self.isa.assembler_directives[directive][0]
                    output_bitlines[idx][4] = list(self.isa.assembler_directives[directive][1])
                    if len(self.isa.assembler_directives[directive]) > 2:
                        output_bitlines[idx][5] = self.isa.assembler_directives[directive][2]

            inst = output_bitlines[idx]
            # instruction encoding
            if isinstance(inst, list):  # still need to encode
                instruction_format = self.isa.opcode_format[self.isa.opcode_map[inst[2]][1]]
                # print(instruction_format)
                # print(output_bitlines[idx])
                out_bv = BitVector(size=0)
                for entry in instruction_format:
                    if 'opcode' in entry[0]:
                        out_bv += self.isa.opcode_map[inst[2]][0]
                    elif 'reg' in entry[0]:
                        out_bv += BitVector(intVal=int(inst[4].pop(0)), size=entry[1])
                    elif 'imm' in entry[0]:
                        out_bv += BitVector(intVal=int(inst[5]), size=entry[1])
                    elif '0' in entry[0]:
                        out_bv += BitVector(size=entry[1])
                output_bitlines[idx] = out_bv

            # print(output_bitlines[idx])
            idx += space

        error = False
        for idx, entry in enumerate(output_bitlines):
            if len(output_bitlines[idx]) != 16:
                risc16_log.fatal(f"unrecognized or erroneous syntax in instruction {idx}: {output_bitlines[idx]}")
                error = True
            self.output.append(entry)
        if error:
            self.output = []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asb = Risc16Assembler()

    # om = asb.isa.opcode_map
    # for op in om:
    #     print("{} | {:4} | ".format(om[op][0], op))
    
    asb.input_assembly('sample.risc16')
    asb.output_binary('sample.risc16.bin')
