import unittest

from pytools.numbertools import get_base, get_multiplier, human_readable, is_number, to_number


class TestNumbertools(unittest.TestCase):
	def test_get_base(self):
		self.assertEqual(get_base(1000), 'K')
		self.assertEqual(get_base(1E-9), 'n')
		self.assertEqual(get_base(0), '')
		self.assertEqual(get_base(1234), 'K')
		self.assertEqual(get_base(123E-5), 'm')

	def test_get_multiplier(self):
		self.assertEqual(get_multiplier('n'), 1E-9)
		self.assertEqual(get_multiplier('K'), 1000)
		self.assertEqual(get_multiplier('T'), 1000000000000)

	def test_human_readable(self):
		# test basic cases
		value = 12345678901234567890
		self.assertEqual(human_readable(1234.123, precision = 6), '1.234123K')
		self.assertEqual(human_readable(0.12345, 'm'), '123.45m')
		self.assertEqual(human_readable(111222333444555, precision = 12) ,'111.222333444555T')
		# test custom bases

		self.assertEqual(human_readable(value, 'B'), '12345678901.23B')

	def test_is_number(self):
		self.assertTrue(is_number(123.456))
		self.assertTrue(is_number('123.456'))
		self.assertFalse(is_number('abc'))

	def test_to_number(self):
		self.assertTrue(to_number('123.456'))
		self.assertTrue(to_number('123..456', None) is None)


if __name__ == "__main__":
	unittest.main()


