import BitVector as b
from collections import deque

class _queue():
    def __init__(self, name='', size=0, length=1, _in=None):
        self.name = name
        self.entry_width = size
        self.depth = length
        self.input = _in
        self.output = _wire(size=self.entry_width)
        self.data = deque([b.BitVector(size=self.entry_width) for c in range(self.depth)])

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


class _register_file():
    pass


class _register(_queue):
    def __init__(self, **kwargs):
        super(_register, self).__init__(**kwargs)
        # creates a queue of length 1


class _wire():
    def __init__(self, size=0):
        self.value = b.BitVector(size=size)

    def set(self, value):
        assert value.size == self.value.size
        self.value = value

    def get(self):
        return self.value


# class _logic():
#     def __init__(self, name='', cycle_delay=1, _in=None):
#         self.name = name
#         self.entry_width = size
#         self.depth = length
#         self.input = _in
#         self.output = _wire(size=self.entry_width)

#     def set_name(self, name):
#         self.name = name

#     def tick(self):
#         self.data.appendleft(self.input.get())
#         self.output.set(self.data.pop())


# class _mux():
#     def __init__(self, name='', inputs=[], control=[]):
#         self.inputs = []

#     def out(self, control):
#         return self.inputs[]