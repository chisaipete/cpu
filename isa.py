import BitVector as b

class isa():
    def __init__(self, name):
        self.name = name
        self.word_width = 0
        self.opcode_map = {}
        self.opcode_format = {}
