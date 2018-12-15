from isa import isa
import BitVector as b

class risc16(isa):
    def __init__(self):
        super(risc16, self).__init__('risc16')
        self.word_width = 16
        self.opcode_map = {
            'ADD'  : b.BitVector(bitstring='000'),
            'ADDI' : b.BitVector(bitstring='001'),
            'NAND' : b.BitVector(bitstring='010'),
            'LUI'  : b.BitVector(bitstring='011'),
            'SW'   : b.BitVector(bitstring='100'),
            'LW'   : b.BitVector(bitstring='101'),
            'BEQ'  : b.BitVector(bitstring='110'),
            'JALR' : b.BitVector(bitstring='111'),
        }
        self.opcode_format = {
            'RRR' : [('opcode',3),('regA',3),('regB',3),('0',4),('regC',3)],
            'RRI' : [('opcode',3),('regA',3),('regB',3),('signImm',7)],
            'RI'  : [('opcode',3),('regA',3),('imm',10)],
        }

if __name__ == "__main__":
    om = risc16().opcode_map
    for op in om:
        print("{} | {:4} | ".format(om[op], op))
