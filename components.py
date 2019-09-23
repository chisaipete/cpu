import sys
import unittest
from collections import OrderedDict


class AND:
    def input(self, _in):
        for item in _in:
            if item == 0:
                return 0
        return 1


class OR:
    def input(self, _in):
        for item in _in:
            if item == 1:
                return 1
        return 0


class NOT:
    def input(self, _in):
        if _in == 1:
            return 0
        else:
            return 1


INV = NOT


class XOR:
    def input(self, _in):
        if sum(_in) == 1:
            return 1
        return 0


class XNOR:
    def input(self, _in):
        if sum(_in) == 1:
            return 0
        return 1


class Logic:
    gates = None
    netlist = None

    def __init__(self, gates=(), netlist=None):
        if netlist:
            self.netlist = Netlist(netlist)
        else:
            self.gates = gates

    def input(self, _in):
        if self.gates:
            return self.feed_gates(_in)
        else:
            return self.feed_netlist(_in)

    def feed_gates(self, _in):
        output = None
        for gate in self.gates:
            output = gate.input(_in)
            _in = output
        return output

    def feed_netlist(self, _in):
        return self.netlist.input(_in)

    def __str__(self):
        return str(self.netlist)


class NAND(Logic):
    def __init__(self):
        super(NAND, self).__init__([AND(), NOT()])


class NOR(Logic):
    def __init__(self):
        super(NOR, self).__init__([OR(), NOT()])


class Netlist:
    def __init__(self, text):
        self.inputs = OrderedDict()
        self.outputs = {}
        self.nets = {}
        self.gates = {}
        self.gid = 0
        if text:
            self.parse(text)

    def parse(self, netlist):
        for line in netlist.split("\n"):
            line = line.strip()
            if line:
                if line.startswith("i"):
                    self.process_input_line(line)
                elif line.startswith("n"):
                    self.process_net_line(line)
                elif line.startswith("o"):
                    self.process_output_line(line)
                elif line.startswith("g"):
                    self.process_gate_line(line)

    def process_input_line(self, line):
        for input_ in line.split()[1].split(','):
            self.inputs[input_] = None

    def process_net_line(self, line):
        for net in line.split()[1].split(','):
            self.nets[net] = None

    def process_output_line(self, line):
        for output in line.split()[1].split(','):
            self.outputs[output] = None

    def process_gate_line(self, line):
        gate = self.get_gate(line.split()[1])
        inputs = line.split()[2].split(',')
        outputs = line.split()[3].split(',')
        self.gates[self.gid] = (gate, inputs, outputs)
        self.gid += 1

    def get_gate(self, name):
        return getattr(sys.modules[__name__], name)

    def input(self, _in):
        for index, key in enumerate(self.inputs):
            self.inputs[key] = _in[index]
        assert all(self.inputs), "not all inputs defined!"
        while not self.all_keys_defined(self.outputs):
            # print(self)
            for gate in self.gates:
                if self.inputs_defined(gate):
                    # print('All inputs defined!')
                    if self.output_to_net(gate):
                        self.nets[self.gates[gate][2][0]] = self.gates[gate][0]().input(tuple([self.get_input_or_net_value(in_) for in_ in self.gates[gate][1]]))
                    else:
                        self.outputs[self.gates[gate][2][0]] = self.gates[gate][0]().input(tuple([self.get_input_or_net_value(in_) for in_ in self.gates[gate][1]]))

        return_value = tuple([self.outputs[o] for o in self.outputs])
        self.clear_ports()
        return return_value

    def output_to_net(self, gate):
        return self.gates[gate][2][0] in self.nets

    def inputs_defined(self, gate):
        # print(gate, self.gates[gate])
        for input_ in self.gates[gate][1]:
            # print(input_, self.get_input_or_net_value(input_))
            if self.get_input_or_net_value(input_) is None:
                return False
        return True

    def get_input_or_net_value(self, signal):
        signal_input =  self.inputs.get(signal)
        signal_net = self.nets.get(signal)

        if signal_input is not None:
            return signal_input
        if signal_net is not None:
            return signal_net

    def clear_ports(self):
        for key in self.inputs:
            self.inputs[key] = None
        for key in self.outputs:
            self.outputs[key] = None

    def all_keys_defined(self, dictionary):
        for key in dictionary:
            if dictionary[key] is None:
                return False
        return True

    def __str__(self):
        return f"inputs: {self.inputs}\noutputs: {self.outputs}\nnets: {self.nets}\ngates: {self.gates}"


class Multiplexor(Logic):
    def __init__(self):
        netlist = '''
        '''
        super(Multiplexor, self).__init__(netlist=netlist)


class Demultiplexor(Logic):
    def __init__(self):
        netlist = '''
        '''
        super(Demultiplexor, self).__init__(netlist=netlist)


class HalfAdder(Logic):
    def __init__(self):
        netlist = '''
        i a,b
        o sum,c_out
        g XOR a,b sum
        g AND a,b c_out
        '''
        super(HalfAdder, self).__init__(netlist=netlist)


class FullAdder(Logic):
    def __init__(self):
        netlist = '''
        i a,b,c_in
        o sum,c_out
        n d,e,f
        g XOR a,b d
        g XOR d,c_in sum
        g AND c_in,d e
        g AND a,b f
        g OR  e,f c_out
        '''
        super(FullAdder, self).__init__(netlist=netlist)


class ComponentTests(unittest.TestCase):
    def test_inv(self):
        a = INV()
        output = a.input(1)
        self.assertEqual(0, output)
        b = NOT()
        output = b.input(0)
        self.assertEqual(1, output)
        output = b.input(1)
        self.assertEqual(0, output)

    def test_and(self):
        a = AND()
        output = a.input((0, 0))
        self.assertEqual(0, output)
        output = a.input((0, 1))
        self.assertEqual(0, output)
        output = a.input((1, 0))
        self.assertEqual(0, output)
        output = a.input((1, 1))
        self.assertEqual(1, output)
        output = a.input((0, 0, 1))
        self.assertEqual(0, output)
        output = a.input((1, 1, 1, 1))
        self.assertEqual(1, output)

    def test_or(self):
        a = OR()
        output = a.input((0, 0))
        self.assertEqual(0, output)
        output = a.input((0, 1))
        self.assertEqual(1, output)
        output = a.input((1, 0))
        self.assertEqual(1, output)
        output = a.input((1, 1))
        self.assertEqual(1, output)

    def test_nand(self):
        a = NAND()
        output = a.input((0, 0))
        self.assertEqual(1, output)
        output = a.input((0, 1))
        self.assertEqual(1, output)
        output = a.input((1, 0))
        self.assertEqual(1, output)
        output = a.input((1, 1))
        self.assertEqual(0, output)

    def test_nor(self):
        a = NOR()
        output = a.input((0, 0))
        self.assertEqual(1, output)
        output = a.input((0, 1))
        self.assertEqual(0, output)
        output = a.input((1, 0))
        self.assertEqual(0, output)
        output = a.input((1, 1))
        self.assertEqual(0, output)

    def test_xor(self):
        a = XOR()
        output = a.input((0, 0))
        self.assertEqual(0, output)
        output = a.input((0, 1))
        self.assertEqual(1, output)
        output = a.input((1, 0))
        self.assertEqual(1, output)
        output = a.input((1, 1))
        self.assertEqual(0, output)

    def test_xnor(self):
        a = XNOR()
        output = a.input((0, 0))
        self.assertEqual(1, output)
        output = a.input((0, 1))
        self.assertEqual(0, output)
        output = a.input((1, 0))
        self.assertEqual(0, output)
        output = a.input((1, 1))
        self.assertEqual(1, output)

    def test_xor_from_nand(self):
        """
      A--------+
      |        NAND--D--+
      NAND--C--+        NAND--Q
      |        NAND--E--+
      B--------+
        """
        a = 1
        b = 0
        ab = NAND()
        a_ab = NAND()
        b_ab = NAND()
        d_e = NAND()

        # 1, 0 -> 1
        c = ab.input((a,b))
        d = a_ab.input((a, c))
        e = b_ab.input((b, c))
        output = d_e.input((d, e))
        self.assertEqual(1, output)

    def test_half_adder(self):
        a = 0
        b = 0
        xor_ = XOR()
        and_ = AND()
        sum_ = xor_.input((a, b))
        carry = and_.input((a, b))
        self.assertEqual(0, sum_)
        self.assertEqual(0, carry)

        self.assertEqual(0, xor_.input((0, 0)))
        self.assertEqual(0, and_.input((0, 0)))

        self.assertEqual(1, xor_.input((0, 1)))
        self.assertEqual(0, and_.input((0, 1)))

        self.assertEqual(1, xor_.input((1, 0)))
        self.assertEqual(0, and_.input((1, 0)))

        self.assertEqual(0, xor_.input((1, 1)))
        self.assertEqual(1, and_.input((1, 1)))

        ha = HalfAdder()
        self.assertEqual((0, 0), ha.input((0, 0)))
        self.assertEqual((1, 0), ha.input((0, 1)))
        self.assertEqual((1, 0), ha.input((1, 0)))
        self.assertEqual((0, 1), ha.input((1, 1)))

    # @unittest.skip
    def test_full_adder(self):
        fa = FullAdder()
        self.assertEqual((0, 0), fa.input((0, 0, 0)))
        self.assertEqual((1, 0), fa.input((0, 0, 1)))
        self.assertEqual((1, 0), fa.input((0, 1, 0)))
        self.assertEqual((0, 1), fa.input((0, 1, 1)))
        self.assertEqual((1, 0), fa.input((1, 0, 0)))
        self.assertEqual((0, 1), fa.input((1, 0, 1)))
        self.assertEqual((0, 1), fa.input((1, 1, 0)))
        self.assertEqual((1, 1), fa.input((1, 1, 1)))


