import os
import logging
assembler_log = logging.getLogger('assembler')


class Assembler:
    def __init__(self, isa):
        self.isa = isa
        self.input_path = None
        self.input = None
        self.output_path = None
        self.output = None
        self.line_breaks = False

    def input_assembly(self, path=None):
        self.input_path = path
        assembler_log.info(f"checking input file {self.input_path}")
        if self.input_path:
            if os.path.exists(self.input_path):
                with open(self.input_path) as ip:
                    self.input = ip.read().split('\n')
                self.parse_assembly()
            else:
                assembler_log.error(f"{self.input_path} doesn't exist, or is inaccessible")
        else:
            assembler_log.error("no input file given")

    def parse_assembly(self):
        if self.input:
            assembler_log.info("parsing input")

    def output_binary(self, path=None):
        self.output_path = path
        assembler_log.info(f"attempting to write binary to {self.output_path}")
        if self.output_path and self.input:
            assembler_log.info(f"writing binary to file: {self.output_path}")
            with open(self.output_path, 'w') as op:
                for line in self.output:
                    if self.line_breaks:
                        op.write(str(line))
                        op.write('\n')
                    else:
                        op.write(str(line))
