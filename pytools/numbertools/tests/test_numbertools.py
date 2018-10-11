"""
	Suite of tests for numbertools
"""
import unittest

from pytools.numbertools import get_base, get_multiplier, human_readable, is_number, to_number


class TestNumbertools(unittest.TestCase):
	""" Class to test numbertools"""
	def test_get_base(self):
		""" Tests get base"""
		self.assertEqual('K', get_base(1000))
		self.assertEqual('n', get_base(1E-9))
		self.assertEqual('', get_base(0))
		self.assertEqual('K', get_base(1234))
		self.assertEqual('m', get_base(123E-5))
		self.assertEqual('u', get_base(1E-6))

	def test_get_multiplier(self):
		"""tests get multiplier"""
		self.assertEqual(get_multiplier('n'), 1E-9)
		self.assertEqual(get_multiplier('K'), 1000)
		self.assertEqual(get_multiplier('T'), 1000000000000)

	def test_human_readable(self):
		# test basic cases
		value = 12345678901234567890
		self.assertEqual('1.234123K', human_readable(1234.123, precision = 6))
		self.assertEqual('123.45m', human_readable(0.12345, 'm'))
		self.assertEqual('111.222333444555T', human_readable(111222333444555, precision = 12))
		self.assertEqual('12.5u', human_readable(12.5E-6, precision = 1))
		self.assertEqual('3.14159', human_readable(3.14159, precision = 5))
		# test custom bases

		self.assertEqual('12345678901.23B', human_readable(value, 'B'))

		self.assertRaises(TypeError, human_readable, self)



	def test_is_number(self):
		""" Tests is_number"""
		self.assertTrue(is_number(123.456))
		self.assertTrue(is_number('123.456'))
		self.assertFalse(is_number('abc'))
		self.assertFalse(is_number(self))
		self.assertFalse(is_number("12.345.345"))

		# Test iterability
		self.assertListEqual([True, True, True], is_number([123, "456", "789.0"]))
		self.assertListEqual([True, False, False, True, False], is_number([18, "18.1.1", self, "11.4", "11/4"]))

	def test_to_number(self):
		# Tests to_number
		self.assertEqual(123.456, to_number('123.456'))
		self.assertEqual(1.43E-4, to_number('.000143'))
		self.assertEqual(12, to_number('12.000'))
		self.assertEqual(12, to_number(12.000))
		self.assertIsNone(to_number('123..456', None))
		self.assertIsNone(to_number(self, None))
		self.assertEqual(19490293480239/1.0, to_number("19490293480239"))


if __name__ == "__main__":
	unittest.main()


