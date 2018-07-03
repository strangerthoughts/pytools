from dataclasses import dataclass
import typing
from pytools.datatools.generate_schema import convert_type_to_schema
import unittest
from schema import Use, Or, And

class ConvertBuiltInTypesToSchema(unittest.TestCase):
	def test_convert_str(self):
		r = convert_type_to_schema(str)
		self.assertEqual(str, r)
	def test_convert_float(self):
		r = convert_type_to_schema(float)
		self.assertEqual(float, r)
	def test_convert_int(self):
		r = convert_type_to_schema(int)
		self.assertEqual(int, r)
	def test_convert_nonetype(self):
		r = convert_type_to_schema(type(None))
		self.assertEqual(type(None), r)

class ConvertTypingToSchema(unittest.TestCase):
	def test_convert_supports_int(self):
		r = convert_type_to_schema(typing.SupportsInt)
		self.assertEqual(str(Use(int)), str(r))
	def test_convert_supports_float(self):
		r = convert_type_to_schema(typing.SupportsFloat)
		self.assertEqual(str(Use(float)), str(r))

	def test_convert_supports_abs(self):
		r = convert_type_to_schema(typing.SupportsAbs)
		self.assertEqual(str(Use(abs)), str(r))

	def test_convert_list_level_1(self):
		r = convert_type_to_schema(typing.List[str])
		self.assertEqual([str], r)

	def test_convert_list_level_2(self):
		r = convert_type_to_schema(typing.List[typing.Union[str,int]])
		self.assertEqual(str([Or(str, int)]), str(r))

	def test_convert_set(self):
		r = convert_type_to_schema(typing.Set[str])
		self.assertEqual(str([str]), str(r))
	def test_convert_dict_level_0(self):
		t = typing.Dict
		r = convert_type_to_schema(t)
		self.assertEqual(typing.Dict[typing.Any,typing.Any], r)


if __name__ == "__main__":
	unittest.main()