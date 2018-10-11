""" Suite for testing the validation functions. May be replaced by attrs at a later date."""
from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Tuple, SupportsFloat, SupportsInt, SupportsAbs, Callable, Any
from pytools.datatools.dataclass_validation import validate_item, validate_dataclass
import unittest


class TestSchemaValidation(unittest.TestCase):
	""" Class to test validation functions."""
	def test_dict_level_0(self):
		""" Tests dict"""
		item = {'a': 1, 'b': 2}
		r = validate_item(item, Dict)
		self.assertTrue(r)
		r = validate_item({'a': 123, None: 4}, Dict)
		self.assertTrue(r)

	def test_optional(self):
		"""Test optional"""
		r = validate_item('abc', Optional[str])
		self.assertTrue(r)
		r2 = validate_item(None, Optional[str])
		self.assertTrue(r2)
		r3 = validate_item(123, Optional[str])
		self.assertFalse(r3)

	def test_union(self):
		""" Tests Union of types"""
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
		""" Tests Tuple"""
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
		""" Tests Any"""
		r = validate_item(self, Any)
		self.assertTrue(r)
		r1 = validate_item('a', Any)
		self.assertTrue(r1)
		r3 = validate_item(abs, Any)
		self.assertTrue(r3)
		r4 = validate_item(None, Any)
		self.assertTrue(r4)

	def test_str(self):
		""" Tests str"""
		r = validate_item('abc', str)
		self.assertTrue(r)
		r2 = validate_item(None, str)
		self.assertFalse(r2)

	def test_int(self):
		""" Tests int"""
		r = validate_item(123, int)
		self.assertTrue(r)
		r2 = validate_item(.123, int)
		self.assertFalse(r2)

	def test_float(self):
		""" Tests float"""
		r = validate_item(123.3, float)
		self.assertTrue(r)
		r2 = validate_item(123, float)
		self.assertFalse(r2)
		r3 = validate_item(123E3, float)
		self.assertTrue(r3)

	def test_supports_float(self):
		"""Tests Supports float"""
		r = validate_item(123.456, SupportsFloat)
		self.assertTrue(r)
		r2 = validate_item(456, SupportsFloat)
		self.assertTrue(r2)
		r3 = validate_item('0.987485', SupportsFloat)
		self.assertTrue(r3)
		r4 = validate_item('abc', SupportsFloat)
		self.assertFalse(r4)
		r5 = validate_item(None, SupportsFloat)
		self.assertFalse(r5)
		r6 = validate_item(self, SupportsFloat)
		self.assertFalse(r6)

	def test_supports_int(self):
		""" Tests supports int"""
		r = validate_item(123, SupportsInt)
		self.assertTrue(r)
		r2 = validate_item(123.456, SupportsInt)
		self.assertTrue(r2)
		r3 = validate_item('123', SupportsInt)
		self.assertTrue(r3)
		r4 = validate_item('abc', SupportsInt)
		self.assertFalse(r4)
		r5 = validate_item(None, SupportsInt)
		self.assertFalse(r5)
		r6 = validate_item(self, SupportsInt)
		self.assertFalse(r6)

	def test_supports_abs(self):
		""" Tests supports abs"""
		r = validate_item(839234, SupportsAbs)
		self.assertTrue(r)
		r2 = validate_item(-123.63463, SupportsAbs)
		self.assertTrue(r2)
		r3 = validate_item('314321', SupportsAbs)
		self.assertFalse(r3)

	def test_callable(self):
		""" Tests callable"""
		r = validate_item(abs, Callable)
		self.assertTrue(r)
		r2 = validate_item(lambda s: s, Callable)
		self.assertTrue(r2)
		r3 = validate_item(int, Callable[[Any], int])
		self.assertTrue(r3)
		r4 = validate_item('assfsaf', Callable)
		self.assertFalse(r4)
		r5 = validate_item('afasfs', Callable[[int], float])
		self.assertFalse(r5)

		class TestA:
			"""dummy class"""
			def __call__(self):
				pass

		class TestB:
			""" dummy class"""
			pass

		r6 = validate_item(TestA(), Callable)
		self.assertTrue(r6)
		r7 = validate_item(TestB, Callable)
		self.assertTrue(r7)
		r8 = validate_item(TestB(), Callable)
		self.assertFalse(r8)


class DataclassTests(unittest.TestCase):
	""" Tests dataclass validation"""
	def test_simple_dataclass(self):
		""" Tests a dataclass with only a few attributes"""
		@dataclass
		class DataClassCard:
			""" dummy dataclass"""
			rank: str
			suit: str

		r = validate_dataclass(DataClassCard('A', 'B'))
		self.assertTrue(r)
		r2 = validate_dataclass(DataClassCard('asfasf', 'aasdasfaf'))
		self.assertTrue(r2)
		# noinspection PyTypeChecker
		r3 = validate_dataclass(DataClassCard(self, 'as'))
		self.assertFalse(r3)

	def test_medium_dataclass(self):
		""" Tests a class with a few more attributes"""
		@dataclass
		class CityMetadata:
			"""dummy dataclass"""
			name: str
			country: str
			latitude: float
			longitude: float
			population: List[Tuple[int, int]]
			area: Dict[str, Union[int, float]]

		@dataclass
		class Country:
			""" dummy attribute"""
			name: str

		area = {
			'total': 1213.37, 'land': 783.84, 'water': 429.53, 'metro': 34490
		}
		population = [(1970, 7894862), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
			(2017, 8660000)]
		city_name = 'New York City'
		country = 'USA'
		latitude = 40.5
		longitude = -40.5

		data = CityMetadata(name = city_name, country = country, latitude = latitude, longitude = longitude,
			population = population, area = area)
		# noinspection PyTypeChecker
		data2 = CityMetadata(name = city_name, country = country, latitude = latitude, longitude = longitude,
			population = population + [(2020, 1234.567)], area = area)
		data3 = CityMetadata(name = city_name, country = country, latitude = latitude, longitude = longitude,
			population = population, area = {**area, **{'test': 'abc'}})
		# noinspection PyTypeChecker
		data4 = CityMetadata(name = city_name, country = Country('USA'), latitude = latitude, longitude = longitude,
			population = population, area = area)
		r = validate_dataclass(data)
		r2 = validate_dataclass(data2)
		r3 = validate_dataclass(data3)
		r4 = validate_dataclass(data4)
		self.assertTrue(r)
		self.assertFalse(r2)
		self.assertFalse(r3)
		self.assertFalse(r4)


if __name__ == "__main__":
	unittest.main()
