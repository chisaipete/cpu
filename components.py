import unittest


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
    def __init__(self, gates=(), netlist=None):
        if netlist:
            self.netlist = netlist
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
        return None


class Netlist:
    def __init__(self, inputs, outputs, nets, gates):
        self.inputs = inputs.split(',')
        self.outputs = outputs.split(',')
        self.nets = [net for net in nets]
        self.gates = []

    def parse(self, netlist):
        assert(len(netlist) == 3)

    def __str__(self):
        return f"inputs: {self.inputs}\noutputs: {self.outputs}\nnets: {self.nets}"


class NAND(Logic):
    def __init__(self):
        super(NAND, self).__init__([AND(), NOT()])


class NOR(Logic):
    def __init__(self):
        super(NOR, self).__init__([OR(), NOT()])


class HalfAdder(Logic):
    def __init(self):

        super(HalfAdder, self).__init__()


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
        n = Netlist("a,b", "s,c", "", [XOR, AND])
        print(n)


