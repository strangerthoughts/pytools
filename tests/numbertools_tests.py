import unittest 

from pytools.numbertools import *


class TestNumbertools(unittest.TestCase):
	def testGetBase(self):

		self.assertTrue(getBase(1000) == 'K')
		self.assertTrue(getBase(1E-9) == 'n')
		self.assertTrue(getBase(0) == '')
	
	def testGetMultiplier(self):
		self.assertTrue(getMultiplier('n') == 1E-9)
		self.assertTrue(getMultiplier('K') == 1000)
		self.assertTrue(getMultiplier('T') == 1000000000000)

	def testHumanReadable(self):
		#test basic cases
		value = 12345678901234567890
		self.assertTrue(humanReadable(1234.123, precision = 6) == '1.234123K')
		self.assertTrue(humanReadable(0.12345, 'm') == '123.45m')
		self.assertTrue(humanReadable(111222333444555, precision = 12) == '111.222333444555T')
		# test custom bases

		self.assertTrue(humanReadable(value, 'B') == '12345678901.23B')

	def testIsNumber(self):
		self.assertTrue(isNumber(123.456))
		self.assertTrue(isNumber('123.456'))

	def testToNumber(self):
		self.assertTrue(toNumber('123.456'))
		self.assertTrue(toNumber('123..456', None) is None)


if __name__ == "__main__":
	unittest.main()

		

