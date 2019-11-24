import argparse
import logging
import os
import sys
from enum import Enum, auto

from hack import Hack
from translator import Translator
hack_log = logging.getLogger('hack')

arithmetic_commands = [
    'add',
    'sub',
    'neg',
]

logical_commands = [
    'eq',
    'gt',
    'lt',
    'and',
    'or',
    'not',
]


class Command(Enum):
    ARITHMETIC = auto()
    PUSH = auto()
    POP = auto()
    LABEL = auto()
    GOTO = auto()
    IF = auto()
    FUNCTION = auto()
    RETURN = auto()
    CALL = auto()


class VMTranslator(Translator):
    def __init__(self):
        super(VMTranslator, self).__init__(Hack())
        self.line_breaks = True
        self.branch_id = 0
        self.current_file = ''
        self.output = []

    def parse_vm(self):
        hack_log.info('translating the hack vm input to hack assembly')
        self.current_file = os.path.splitext(os.path.basename(self.input_path))[0]
        for line in self.input:
            line = line.strip()
            if line:
                removed_comments = line.strip().split('//')[0].strip()
                if removed_comments:
                    try:
                        command_type, segment, index = self.decode_command(line)
                        operation = segment
                        label = segment
                        local_vars = index
                    except TypeError:
                        hack_log.error(f"unrecognized line: {line}")
                        sys.exit()
                    print(f"{command_type} {line}")
                    if command_type == Command.ARITHMETIC:
                        self.output.extend(self.write_arithmetic(operation))
                    elif command_type == Command.PUSH:
                        self.output.extend(self.write_push(segment, index))
                    elif command_type == Command.POP:
                        self.output.extend(self.write_pop(segment, index))
                    elif command_type == Command.LABEL:
                        self.output.extend(self.write_label(label))
                    elif command_type == Command.IF:
                        self.output.extend(self.write_if_goto(label))
                    elif command_type == Command.GOTO:
                        self.output.extend(self.write_goto(label))
                    elif command_type == Command.FUNCTION:
                        self.output.extend(self.write_function(label, local_vars))

    def set_file_name(self, file_name):
        self.current_file = file_name

    @staticmethod
    def decode_command(line):
        sp_line = line.split()
        if sp_line[0] == 'push':
            return Command.PUSH, sp_line[1], sp_line[2]
        if sp_line[0] == 'pop':
            return Command.POP, sp_line[1], sp_line[2]
        if sp_line[0] in arithmetic_commands + logical_commands:
            return Command.ARITHMETIC, sp_line[0], None
        if sp_line[0] == 'label':
            return Command.LABEL, sp_line[1], None
        if sp_line[0] == 'if-goto':
            return Command.IF, sp_line[1], None
        if sp_line[0] == 'goto':
            return Command.GOTO, sp_line[1], None
        if sp_line[0] == 'function':
            return Command.FUNCTION, sp_line[1], sp_line[2]

    def write_init(self):
        pass

    @staticmethod
    def write_label(label):
        return [f"({label})"]

    @staticmethod
    def write_goto(label):
        return [
            f'@{label}', '0;JMP'
        ]

    @staticmethod
    def write_if_goto(label):
        return [
            # D = *(SP--)
            '@SP', 'AM=M-1', 'D=M',
            # if D: goto label  (D < 0 -> (D=-1 true)
            f'@{label}', 'D;JGT',
        ]

    def write_function(self, function_name, number_of_variables):
        pass

    def write_call(self, function_name, number_of_arguments):
        pass

    def write_return(self):
        pass

    def write_arithmetic(self, command):
        # TODO: optionally print comments
        assembly = [f'// {command}']
        if command == 'add':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # # push x + y
                # *SP=D+*SP
                'A=M', 'M=D+M',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'sub':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # # push x - y
                # *SP=D-*SP
                'A=M', 'M=M-D',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'neg':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # # push -y
                # *SP=-D
                'A=M', 'M=-M',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'and':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # # push x & y
                # *SP=D&*SP
                'A=M', 'M=D&M',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'or':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # # push x | y
                # *SP=D|*SP
                'A=M', 'M=D|M',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'not':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # # push !y
                # *SP=!D
                'A=M', 'M=!M',
                # SP++
                '@SP', 'M=M+1'
            ])

        elif command == 'eq':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # if D==0 JNE -> (not_equal)
                'A=M', 'D=D-M', f'@NOT_EQ_{self.branch_id}', 'D;JNE',
                # *(SP) = -1
                '@SP', 'A=M', 'M=-1', f'@END_EQ_{self.branch_id}', '0;JMP',
                #(not_equal) *SP = 0
                f'(NOT_EQ_{self.branch_id})', '@SP', 'A=M', 'M=0',
                #(end_equal) SP++
                f'(END_EQ_{self.branch_id})', '@SP', 'M=M+1'
            ])
            self.branch_id += 1

        elif command == 'lt':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # if D < 0 JLE -> (not_lt)
                'A=M', 'D=D-M', f'@NOT_LT_{self.branch_id}', 'D;JLE',
                # *(SP) = -1
                '@SP', 'A=M', 'M=-1', f'@END_LT_{self.branch_id}', '0;JMP',
                # (not_lt) *SP = 0
                f'(NOT_LT_{self.branch_id})', '@SP', 'A=M', 'M=0',
                # (end_lt) SP++
                f'(END_LT_{self.branch_id})', '@SP', 'M=M+1'
            ])
            self.branch_id += 1

        elif command == 'gt':
            assembly.extend([
                # # pop y
                # SP--
                '@SP', 'M=M-1',
                # D=*SP
                'A=M', 'D=M',
                # # 'pop' x
                # SP--
                '@SP', 'M=M-1',
                # if D > 0 JGE -> (not_gt)
                'A=M', 'D=D-M', f'@NOT_GT_{self.branch_id}', 'D;JGE',
                # *(SP) = -1
                '@SP', 'A=M', 'M=-1', f'@END_GT_{self.branch_id}', '0;JMP',
                # (not_gt) *SP = 0
                f'(NOT_GT_{self.branch_id})', '@SP', 'A=M', 'M=0',
                # (end_gt) SP++
                f'(END_GT_{self.branch_id})', '@SP', 'M=M+1'
            ])
            self.branch_id += 1

        return assembly

    def write_push(self, segment, index):
        # TODO: optionally print comments
        assembly = [f'// push {segment} {index}']
        if segment == 'constant':
            assembly.extend([
                # # D=index
                f'@{int(index)}', 'D=A',
                # # *SP=D
                '@SP', 'A=M', 'M=D',
                # # SP++
                '@SP', 'M=M+1'
            ])
        else:
            if segment == 'pointer':
                if index == '0':
                    assembly.append('@THIS')
                elif index == '1':
                    assembly.append('@THAT')
                assembly.extend([
                    'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'
                ])
            elif segment == 'static':
                assembly.append(f'@{self.current_file}.{index}')
                assembly.extend([
                    'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'
                ])
            else:
                if segment == 'temp':
                    assembly.append('@5')
                else:
                    if segment == 'local':
                        assembly.append('@LCL')
                    elif segment == 'argument':
                        assembly.append('@ARG')
                    elif segment == 'this':
                        assembly.append('@THIS')
                    elif segment == 'that':
                        assembly.append('@THAT')
                    assembly.append('A=M')

                assembly.extend([
                    # # addr = segment + index
                    'D=A', f'@{index}', 'A=D+A',
                    # # *SP = *addr
                    'D=M', '@SP', 'A=M', 'M=D',
                    # # SP++
                    '@SP', 'M=M+1'
                ])

        return assembly

    def write_pop(self, segment, index):
        # TODO: optionally print comments
        assembly = [f'// pop {segment} {index}']
        if segment == 'pointer':
            assembly.extend([
                '@SP', 'AM=M-1', 'D=M',
            ])
            if index == '0':
                assembly.append('@THIS')
            elif index == '1':
                assembly.append('@THAT')
            assembly.extend([
                'M=D'
            ])
        elif segment == 'static':
            assembly.extend([
                '@SP', 'AM=M-1', 'D=M',
            ])
            assembly.append(f'@{self.current_file}.{index}')
            assembly.extend([
                'M=D'
            ])
        else:
            if segment == 'temp':
                assembly.append('@5')
            else:
                if segment == 'local':
                    assembly.append('@LCL')
                elif segment == 'argument':
                    assembly.append('@ARG')
                elif segment == 'this':
                    assembly.append('@THIS')
                elif segment == 'that':
                    assembly.append('@THAT')
                assembly.append('A=M')
            assembly.extend([
                # # addr = segment + index
                'D=A', f'@{index}', 'D=D+A',
                # # pop y
                '@SP', 'M=M-1',
                # # *addr = *SP
                '@R13', 'M=D', '@SP', 'A=M', 'D=M', '@R13', 'A=M', 'M=D'
            ])

        return assembly


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="""""", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,max_help_position=80))
    parser.add_argument('vm_src', metavar='xxx.vm', type=str, nargs='?', help='vm file / directory to convert')
    args = parser.parse_args()

    if args.vm_src:
        if os.path.isfile(args.vm_src) and args.vm_src.endswith('.vm'):
            vmt = VMTranslator()
            vmt.input_vm(args.vm_src)
            vmt.output_assembly(args.vm_src.replace('.vm', '.asm'))
        elif os.path.isdir(args.vm_src):
            vm_output_assembly = os.path.join(args.vm_src, args.vm_src + '.asm')
            with open(vm_output_assembly, 'w') as oa:
                for file in os.listdir(args.vm_src):
                    if os.path.isfile(file) and file.endswith('.vm'):
                        vmt = VMTranslator()
                        vmt.input_vm(file)
                        vmt.output_assembly(vm_output_assembly, oa)
