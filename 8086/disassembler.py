import logging
import struct
import sys
from pathlib import Path

from common.isa import Isa

log = logging.getLogger("8086")


class Intel8086(Isa):
    def __init__(self):
        super().__init__("8086")
        self.word_size = 8

        self.op_code = {  # opcode, mnemonic, mask
            0b10001000: ("mov", "rm_2f_r", 0b11111100),  # reg/mem to/from reg
            0b11000110: ("mov",  "i_2_rm", 0b11111110),  # imm to reg/mem
            0b10110000: ("mov",   "i_2_r", 0b11110000),  # imm to reg
            0b10100000: ("mov",   "m_2_a", 0b11111110),  # mem to acc
            0b10100010: ("mov",   "a_2_m", 0b11111110),  # acc to mem
        }
        self.d = 0b00000010  # 0 = src in reg; 1 = dst in reg
        self.w = 0b00000001  # 0 = byte data;  1 = word data
        self.s = b""
        self.v = b""
        self.z = b""

        self.mod = 0b11000000

        self.reg = 0b00111000
        self.r_m = 0b00000111

        self.reg_code = {  # register-mask, mnemonic (w bit indexed)
            0b000: ["al", "ax"],
            0b001: ["cl", "cx"],
            0b010: ["dl", "dx"],
            0b011: ["bl", "bx"],
            0b100: ["ah", "sp"],
            0b101: ["ch", "bp"],
            0b110: ["dh", "si"],
            0b111: ["bh", "di"],
        }

        self.r_m_code = {  # r/m mask, eff-add calc terms (mod indexed)
            0b000: {
                0b00: ["bx", "si"],
                0b01: ["bx", "si",  "d8"],
                0b10: ["bx", "si", "d16"],
            },
            0b001: {
                0b00: ["bx", "di"],
                0b01: ["bx", "di",  "d8"],
                0b10: ["bx", "di", "d16"],
            },
            0b010: {
                0b00: ["bp", "si"],
                0b01: ["bp", "si",  "d8"],
                0b10: ["bp", "si", "d16"],
            },
            0b011: {
                0b00: ["bp", "di"],
                0b01: ["bp", "di",  "d8"],
                0b10: ["bp", "di", "d16"],
            },
            0b100: {
                0b00: ["si"],
                0b01: ["si", "d8"],
                0b10: ["si", "d16"],
            },
            0b101: {
                0b00: ["di"],
                0b01: ["di", "d8"],
                0b10: ["di", "d16"],
            },
            0b110: {
                0b00: ["d-add"],
                0b01: ["bp", "d8"],
                0b10: ["bp", "d16"],
            },
            0b111: {
                0b00: ["bx"],
                0b01: ["bx", "d8"],
                0b10: ["bx", "d16"],
            },
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
        op = ("", "")
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
        data_lo = 0b00000000
        data_hi = 0b00000000
        addr_lo = 0b00000000
        addr_hi = 0b00000000
        disp_lo = 0b00000000
        disp_hi = 0b00000000

        for b in self.binary:

            log.debug(f"> byte: {b:b} [{byte_count}]")

            if byte_count == 0:  # opcode byte

                op = ("", "")
                src_in_reg = False
                dst_in_reg = False
                byte_data = False
                word_data = False
                mem_mode_no_disp = False
                mem_mode_8b_disp = False
                mem_mode_16b_disp = False
                reg_mode = False
                data_lo = 0b00000000
                data_hi = 0b00000000
                addr_lo = 0b00000000
                addr_hi = 0b00000000
                disp_lo = 0b00000000
                disp_hi = 0b00000000

                for _op in self.isa.op_code:
                    # log.debug(f"{b:b} & {_op:b} = {b & _op:b}")
                    mask = self.isa.op_code[_op][2]
                    if (b & mask) == _op:
                        op = self.isa.op_code[_op]
                        log.debug(f"    OP: {op[0]} ({op[1]})")
                        byte_count += 1
                        break

                if op[0] == "mov":
                    if op[1] == "rm_2f_r":
                        dst_in_reg = ((b & self.isa.d) >> 1) == 1
                        src_in_reg = not dst_in_reg
                        log.debug(f"     D: {dst_in_reg:b}  REG = {'src' if src_in_reg else 'dst'}")

                    if op[1] in {"rm_2f_r", "i_2_rm", "i_2_r", "m_2_a", "a_2_m"}:
                        if op[1] in {"rm_2f_r", "i_2_rm", "m_2_a", "a_2_m"}:
                            byte_data = (b & self.isa.w) == 0
                            word_data = not byte_data
                        elif op[1] == "i_2_r":
                            byte_data = (b & (self.isa.w << 3)) == 0
                            word_data = not byte_data
                        log.debug(f"     W: {word_data:b} data = {'byte' if byte_data else 'word'}")

                    if op[1] == "i_2_r":
                        reg = b & 0b111
                        reg_d = self.isa.reg_code[reg][1 if word_data else 0]
                        log.debug(f"   REG: {reg:b} {reg_d}")

            elif byte_count == 1:
                if op[0] == "mov":
                    if op[1] in {"rm_2f_r", "i_2_rm"}:  # mod-rm byte
                        mod = (b & self.isa.mod) >> 6
                        if mod == 0b00:
                            mem_mode_no_disp = True
                        elif mod == 0b01:
                            mem_mode_8b_disp = True
                        elif mod == 0b10:
                            mem_mode_16b_disp = True
                        elif mod == 0b11:
                            reg_mode = True

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

                        if op[1] == "rm_2f_r":
                            reg = (b & self.isa.reg) >> 3
                            reg_d = self.isa.reg_code[reg][1 if word_data else 0]
                            log.debug(f"   REG: {reg:b} {reg_d}")
                        elif op[1] == "i_2_rm":
                            reg = 0b000

                        r_m = b & self.isa.r_m
                        r_m_d = ""
                        r_m_c = ""
                        if mod == 0b11:
                            r_m_d = self.isa.reg_code[r_m][1 if word_data else 0]
                        else:
                            r_m_c = "["
                            for i, opr in enumerate(self.isa.r_m_code[r_m][mod]):
                                if i > 0:
                                    r_m_c += " + "
                                r_m_c += f"{opr}"
                            r_m_c += "]"

                        log.debug(f"   R/M: {r_m:b} {r_m_d if reg_mode else r_m_c}")

                        if reg_mode:
                            if dst_in_reg:
                                dst = reg_d
                                src = r_m_d
                            else:
                                dst = r_m_d
                                src = reg_d
                            self.assembly.append(f"{op[0]} {dst}, {src}")
                            log.debug(f" > {self.assembly[-1]}")
                            byte_count = 0

                        elif mem_mode_no_disp:
                            if dst_in_reg:
                                dst = reg_d
                                src = r_m_c
                            else:
                                dst = r_m_c
                                src = reg_d
                            self.assembly.append(f"{op[0]} {dst}, {src}")
                            log.debug(f" > {self.assembly[-1]}")
                            byte_count = 0

                        elif mem_mode_8b_disp:
                            byte_count += 1

                        elif mem_mode_16b_disp:
                            byte_count += 1

                    if op[1] == "i_2_r":
                        data_lo = b
                        log.debug(f"  DATA: {data_lo:b} ({data_lo})")
                        if byte_data:
                            self.assembly.append(f"{op[0]} {reg_d}, {data_lo}")
                            log.debug(f" > {self.assembly[-1]}")
                            byte_count = 0
                        elif word_data:
                            byte_count += 1

            elif byte_count == 2:
                if op[0] == "mov":
                    if op[1] == "rm_2f_r":
                        disp_lo = b
                        log.debug(f" DISPL: {disp_lo:b} ({disp_lo})")
                        if mod == 0b01:
                            if src_in_reg:
                                self.assembly.append(f"{op[0]} {r_m_c.replace('d8', str(disp_lo)).replace(' + 0]', ']')}, {reg_d}")
                            else:
                                self.assembly.append(f"{op[0]} {reg_d}, {r_m_c.replace('d8', str(disp_lo)).replace(' + 0]', ']')}")
                            log.debug(f" > {self.assembly[-1]}")
                            byte_count = 0
                        elif mod == 0b10:
                            byte_count += 1

                    elif op[1] == "i_2_r":
                        data_hi = b
                        log.debug(f"  DATA: {data_hi:b} ({data_hi})")
                        self.assembly.append(f"{op[0]} {reg_d}, {data_lo + (data_hi << 8)}")
                        log.debug(f" > {self.assembly[-1]}")
                        byte_count = 0

            elif byte_count == 3:
                if op[0] == "mov":
                    if op[1] == "rm_2f_r":
                        disp_hi = b
                        log.debug(f" DISPH: {disp_hi:b} ({disp_hi})")
                        if mod == 0b10:
                            self.assembly.append(f"{op[0]} {reg_d}, {r_m_c.replace('d16', str(disp_lo + (disp_hi << 8)))}")
                            log.debug(f" > {self.assembly[-1]}")
                            byte_count = 0

            elif byte_count == 4:
                pass

            elif byte_count == 6:
                pass

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
