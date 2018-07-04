from dataclasses import dataclass
from typing import *
from pytools.datatools.dataclass_validation import validate_item
import unittest


class TestSchemaValidation(unittest.TestCase):
	def test_dict_level_0(self):
		item = {'a': 1, 'b': 2}
		r = validate_item(item, Dict)
		self.assertTrue(r)
		r = validate_item({'a': 123, None: 4}, Dict)
		self.assertTrue(r)

	def test_optional(self):
		r = validate_item('abc', Optional[str])
		self.assertTrue(r)
		r2 = validate_item(None, Optional[str])
		self.assertTrue(r2)
		r3 = validate_item(123, Optional[str])
		self.assertFalse(r3)

	def test_union(self):
		r = validate_item(123.0, Union[str, float])
		self.assertTrue(r)
		r2 = validate_item('abc', Union[str, float])
		self.assertTrue(r2)
		r3 = validate_item(3.14, Union[str, float])
		self.assertTrue(r3)
		r4 = validate_item(3, Union[str, float])
		self.assertFalse(r4)
		r5 = validate_item(123, Union[str, None])
		self.assertFalse(r5)

	def test_tuple(self):
		r = validate_item((1, 2, 3), Tuple[int, int, int])
		self.assertTrue(r)
		r2 = validate_item((1, 'b', 3), Tuple[int, str, int])
		self.assertTrue(r2)
		r3 = validate_item((1, 3.14, 5), Tuple[int, Union[str, float], int])
		self.assertTrue(r3)

		r4 = validate_item((1, 2, 3), Tuple[int, int])
		self.assertFalse(r4)
		r5 = validate_item((1, 'b', 'c'), Tuple[int, str, int])
		self.assertFalse(r5)

	def test_any(self):
		r = validate_item(self, Any)
		self.assertTrue(r)
		r1 = validate_item('a', Any)
		self.assertTrue(r1)
		r3 = validate_item(abs, Any)
		self.assertTrue(r3)
		r4 = validate_item(None, Any)
		self.assertTrue(r4)

	def test_callable(self):
		r = validate_item(abs, Callable)
		self.assertTrue(r)
		r2 = validate_item(abs, Callable[[Any], bool])
		self.assertTrue(r2)
	def test_str(self):
		r = validate_item('abc', str)
		self.assertTrue(r)
		r2 = validate_item(None, str)
		self.assertFalse(r2)
	def test_int(self):
		r = validate_item(123, int)
		self.assertTrue(r)
		r2 = validate_item(.123, int)
		self.assertFalse(r2)
	def test_float(self):
		r = validate_item(123.3, float)
		self.assertTrue(r)
		r2 = validate_item(123, float)
		self.assertFalse(r2)
		r3 = validate_item(123E3, float)
		self.assertTrue(r3)


if __name__ == "__main__":
	unittest.main()
