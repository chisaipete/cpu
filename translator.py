import os
import logging
translator_log = logging.getLogger('translator')


class Translator:
    def __init__(self, isa):
        self.isa = isa
        self.input_path = None
        self.input = None
        self.output_path = None
        self.output = None
        self.line_breaks = False

    def input_vm(self, path=None):
        self.input_path = path
        translator_log.info(f"checking input file {self.input_path}")
        if self.input_path:
            if os.path.exists(self.input_path):
                with open(self.input_path) as ip:
                    self.input = ip.read().split('\n')
                self.parse_vm()
            else:
                translator_log.error(f"{self.input_path} doesn't exist, or is inaccessible")
        else:
            translator_log.error("no input file given")

    def parse_vm(self):
        if self.input:
            translator_log.info("parsing input")

    def output_assembly(self, path=None):
        self.output_path = path
        translator_log.info(f"attempting to write assembly to {self.output_path}")
        if self.output_path and self.input:
            translator_log.info(f"writing assembly to file: {self.output_path}")
            with open(self.output_path, 'w') as op:
                for line in self.output:
                    if self.line_breaks:
                        op.write(str(line))
                        op.write('\n')
                    else:
                        op.write(str(line))
