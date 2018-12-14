#!/usr/bin/env python
import BitVector

opcode_map = {
	
}

class instruction():
	def __init__(self, opcode, destination=(), source=(), immediate=()):
		# opcode = n-bit vector
		# destination = tuple (number, names)
		# source = tuple (number, names)
		# immediate = tuple (number, names)
		self.opcode = opcode
		self.destination = destination
		self.source = source
		self.immediate = immediate

