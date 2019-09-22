from isa import Isa
from assembler import Assembler
import logging
from BitVector import BitVector
hack_log = logging.getLogger('hack')
from pprint import pprint


class Hack(Isa):
    def __init__(self):
        super(Hack, self).__init__('hack')
        self.word_size = 16
        self.opcode_map = {
        }

        self.opcode_format = {
        }

        self.assembler_directives = {
        }


class HackAssembler(Assembler):
    def __init__(self):
        super(HackAssembler, self).__init__(Hack())

    def parse_assembly(self):
        hack_log.info('applying the hack assembly format to input')
        self.output = []
        symbol_table = {}
        instruction_count = 0
        output_bitlines = []



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asb = HackAssembler()

    # om = asb.isa.opcode_map
    # for op in om:
    #     print("{} | {:4} | ".format(om[op][0], op))
    
    asb.input_assembly('sample.hasm')
    asb.output_binary('sample.hack')
