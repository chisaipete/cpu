import logging
import sys
from pathlib import Path

from common.isa import Isa

log = logging.getLogger("8086")


class Intel8086(Isa):
    def __init__(self):
        super().__init__("8086")
        self.word_size = 8

        self.opcode = {  # opcode-mask, mnemonic
            0b100010: "mov"
        }
        self.d = 0b00000010  # 0 = src in reg; 1 = dst in reg
        self.w = 0b00000001  # 0 = byte data;  1 = word data
        self.s = b""
        self.v = b""
        self.z = b""

        self.mod = 0b11000000

        self.reg = 0b00111000
        self.r_m = 0b00000111

        self.regcode = {  # register-mask, mnemonic (w bit indexed)
            0b000: ["al", "ax"],
            0b001: ["cl", "cx"],
            0b010: ["dl", "dx"],
            0b011: ["bl", "bx"],
            0b100: ["ah", "sp"],
            0b101: ["ch", "bp"],
            0b110: ["dh", "si"],
            0b111: ["bh", "di"],
        }


class Disassembler:
    def __init__(self):
        self.path = None
        self.binary = None
        self.assembly = []
        self.isa = Intel8086()

    def input_binary(self, path: Path):
        self.path = path
        self.binary = self.path.read_bytes()
        self._disassemble()

    def _disassemble(self):
        log.debug(self.binary)
        byte_count = 0

        line = ""
        op = None
        # D bit
        src_in_reg = False
        dst_in_reg = False
        # W bit
        byte_data = False
        word_data = False
        # MOD field
        mem_mode_no_disp = False
        mem_mode_8b_disp = False
        mem_mode_16b_disp = False
        reg_mode = False

        for b in self.binary:
            log.debug(f"> byte: {b:b}")
            if byte_count == 0:  # opcode byte
                op = ""
                src_in_reg = False
                dst_in_reg = False
                byte_data = False
                word_data = False
                for _op in self.isa.opcode:
                    if b >> 2 == _op:
                        op = self.isa.opcode[_op]
                        log.debug(f"    OP: {op}")
                        byte_count += 1
                        break
                dst_in_reg = (b & self.isa.d) == 1
                src_in_reg = not dst_in_reg
                byte_data = (b & self.isa.w) == 0
                word_data = not byte_data
                log.debug(f"     D: {dst_in_reg:b}  REG = {'src' if src_in_reg else 'dst'}")
                log.debug(f"     W: {word_data:b} data = {'byte' if byte_data else 'word'}")

            elif byte_count == 1:  # mod-rm byte
                mod = (b & self.isa.mod) >> 6
                if mod == 0b00:
                    mem_mode_no_disp = True
                elif mod == 0b01:
                    mem_mode_8b_disp = True
                elif mod == 0b10:
                    mem_mode_16b_disp = True
                elif mod == 0b11:
                    reg_mode = True
                reg = (b & self.isa.reg) >> 3
                r_m = (b & self.isa.r_m)
                mode_string = ""
                if mem_mode_16b_disp or mem_mode_8b_disp or mem_mode_no_disp:
                    mode_string = "mmode"
                    if mem_mode_no_disp:
                        mode_string += "-no-disp"
                    elif mem_mode_8b_disp:
                        mode_string += "-8b-disp"
                    elif mem_mode_16b_disp:
                        mode_string += "-16b-disp"
                if reg_mode:
                    mode_string = "rmode-no-disp"

                log.debug(f"   MOD: {mod:b} {mode_string}")
                reg_d = self.isa.regcode[reg][1 if word_data else 0]
                r_m_d = self.isa.regcode[r_m][1 if word_data else 0]
                log.debug(f"   REG: {reg:b} {reg_d}")
                log.debug(f"   R/M: {r_m:b} {r_m_d}")

                if op == "mov":
                    if dst_in_reg:
                        dst = reg_d
                        src = r_m_d
                    else:
                        dst = r_m_d
                        src = reg_d
                    self.assembly.append(f"{op} {dst}, {src}")
                    byte_count = 0

    def output_disassembly(self):
        output = f"; {self.path.name} disassembly:\nbits 16\n\n"
        for line in self.assembly:
            output += f"{line}\n"
        return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    dsb = Disassembler()

    in_file = sys.argv[1]
    bin_in = Path(f"../input/perfaware/part1/{in_file}")
    asm_out = Path("../output") / f"{bin_in.name}.asm"

    dsb.input_binary(path=bin_in)
    asm_out.write_text(dsb.output_disassembly())
