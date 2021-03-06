from BitVector import BitVector
from collections import deque


class Queue:
    def __init__(self, name='', size=0, length=1, _in=None):
        self.name = name
        self.entry_width = size
        self.depth = length
        self.input = _in
        self.output = Wire(size=self.entry_width)
        self.data = deque([BitVector(size=self.entry_width) for c in range(self.depth)])

    def set_name(self, name):
        self.name = name

    def tick(self):
        self.data.appendleft(self.input.get())
        self.output.set(self.data.pop())

    def __str__(self):
        r = f'{self.name}\n'
        index_width = len(str(self.depth))
        for i, e in enumerate(self.data):
            r += ("{:"+str(index_width)+"} | {!s}\n").format(i, e)
        return r


class RegisterFile:
    pass


class Register(Queue):
    def __init__(self, **kwargs):
        super(Register, self).__init__(**kwargs)
        # creates a queue of length 1


class Wire:
    def __init__(self, size=0):
        self.value = BitVector(size=size)

    def set(self, value):
        assert value.size == self.value.size
        self.value = value

    def get(self):
        return self.value


# class Logic:
#     def __init__(self, name='', cycle_delay=1, _in=None):
#         self.name = name
#         # self.entry_width = size
#         # self.depth = length
#         self.input = _in
#         # self.output = _wire(size=self.entry_width)
#
#     def set_name(self, name):
#         self.name = name
#
#     def tick(self):
#         self.data.appendleft(self.input.get())
#         self.output.set(self.data.pop())


# class Mux:
#     def __init__(self, name='', inputs=[], control=[]):
#         self.inputs = []
#
#     def out(self, control):
#         return self.inputs
