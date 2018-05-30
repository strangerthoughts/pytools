import unittest

from pytools.numbertools import get_base, get_multiplier, human_readable, is_number, to_number


class TestNumbertools(unittest.TestCase):
	def testGetBase(self):
		self.assertTrue(get_base(1000) == 'K')
		self.assertTrue(get_base(1E-9) == 'n')
		self.assertTrue(get_base(0) == '')

	def testGetMultiplier(self):
		self.assertTrue(get_multiplier('n') == 1E-9)
		self.assertTrue(get_multiplier('K') == 1000)
		self.assertTrue(get_multiplier('T') == 1000000000000)

	def testHumanReadable(self):
		# test basic cases
		value = 12345678901234567890
		self.assertTrue(human_readable(1234.123, precision = 6) == '1.234123K')
		self.assertTrue(human_readable(0.12345, 'm') == '123.45m')
		self.assertTrue(human_readable(111222333444555, precision = 12) == '111.222333444555T')
		# test custom bases

		self.assertTrue(human_readable(value, 'B') == '12345678901.23B')

	def testIsNumber(self):
		self.assertTrue(is_number(123.456))
		self.assertTrue(is_number('123.456'))

	def testToNumber(self):
		self.assertTrue(to_number('123.456'))
		self.assertTrue(to_number('123..456', None) is None)


if __name__ == "__main__":
	unittest.main()


