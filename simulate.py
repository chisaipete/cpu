#!/usr/bin/env python
import argparse
import logging
from constructs import Register, Wire
import BitVector as b
logging.basicConfig(level=logging.INFO)
simulator_log = logging.getLogger('simulator')
# instantiate all modules in the CPU
# connect up all signals between modules (pipeline?)
# load code from memory
# go! (simulate clock ticks simultaneously across all modules)

tick_count = 0
tick_list = []


def state():
    print(f"TICK: {tick_count}")
    for x in tick_list:
        print(x)


def tick():
    global tick_count
    tick_count += 1
    for x in tick_list:
        x.tick()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""""", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,max_help_position=80))
    parser.add_argument('--arch', '-a', action='store', help="architecture to run", required=True)
    parser.add_argument('--code', '-c', action='store', help="assembly code to run", required=True)
    args = parser.parse_args()

    if args.arch == 'risc16':
        from risc16 import *
        asb = Risc16Assembler()
        asb.input_assembly(args.code)

    pc_value = Wire(size=asb.isa.word_size)
    fetched_instruction = Wire(size=asb.isa.word_size)

    PC = Register(name='Program Counter', size=asb.isa.word_size, _in=pc_value)
    tick_list.append(PC)

### FETCH ###

    instruction_memory = asb.output
    FD_inst = Register(name='Fetched Instruction', size=asb.isa.word_size, _in=fetched_instruction)
    FD_pc = Register(name='Fetch/Decode PC', size=asb.isa.word_size, _in=PC.output)
    tick_list.extend([FD_pc, FD_inst])

### DECODE ###

    DE_pc = Register(name='Decode/Execute PC', size=asb.isa.word_size, _in=FD_pc.output)
    tick_list.append(DE_pc)

### EXECUTE ###
    EM_pc = Register(name='Execute/Memory PC', size=asb.isa.word_size, _in=DE_pc.output)
    tick_list.append(EM_pc)

### MEMORY ###
    # data_mux = _logic()
    # MW_wd = _register(name='Memory/Writeback Write Data', size=asb.isa.word_size, _in=)

### WRITEBACK ###

## RUN ##
    pc = 0
    state()
    for i in range(5):
        pc_value.set(b.BitVector(intVal=pc, size=asb.isa.word_size))
        tick()
        state()
        pc += 1
    state()
