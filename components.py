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
    def __init__(self, gates=[]):
        self.gates = gates

    def input(self, _in):
        output = None
        for gate in self.gates:
            output = gate.input(_in)
            _in = output
        return output


class NAND(Logic):
    def __init__(self):
        super(NAND, self).__init__([AND(), NOT()])


class NOR(Logic):
    def __init__(self):
        super(NOR, self).__init__([OR(), NOT()])


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
