import unittest
#from dataclasses import dataclass
from typing import List, Tuple, Union, Dict
from pytools.datatools import dataclass


@dataclass
class City:
	name: str
	latitude: float
	longitude: float
	population: List[Tuple[int, int]]
	area: Dict[str, Union[int, float]]

@dataclass
class Country:
	name: str
	population: int
	cities: List[City]

@dataclass
class CityWrapped:
	name: str
	latitude: float
	longitude: float
	population: List[Tuple[int, int]]
	area: Dict[str, Union[int, float]]

@dataclass
class CountryWrapped:
	name: str
	population: int
	cities: List[CityWrapped]


class TestDataclassResponseBase(unittest.TestCase):
	def setUp(self):
		population = [(1970, 7894862), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
			(2017, 8660000)]
		self.city = City(
			name = 'New York City',
			latitude = 40.0,
			longitude = -40.5,
			population = population,
			area = {
				'total': 1213.37,
				'land':  783.84,
				'water': 429.53,
				'metro': 34490
			}
		)
		self.country = Country(
			name = 'USA',
			population = 328000000,
			cities = [self.city]
		)

	def test_dataclass_fields(self):
		fields = self.city.fields()
		annotations = self.city.__annotations__
		self.assertDictEqual(annotations, fields)

	def test_dataclass_get(self):
		r = self.city.get('name')
		self.assertEqual('New York City', r)
		r2 = self.city.get('fips_code')
		self.assertIsNone(r2)
		r3 = self.city.get(self, 'not found')
		self.assertEqual('not found', r3)

	def test_dataclass_keys(self):
		expected_keys = ['name', 'latitude', 'longitude', 'population', 'area']
		self.assertListEqual(expected_keys, list(self.city.keys()))

	def test_dataclass_values(self):
		expected_values = ['New York City', 40.0, -40.5, self.city.population, self.city.area]
		self.assertListEqual(expected_values, self.city.values())

	def test_dataclass_items(self):
		expected_value = [
			('name', 'New York City'),
			('latitude', 40.0),
			('longitude', -40.5),
			('population', self.city.population),
			('area', self.city.area)
		]
		self.assertListEqual(expected_value, list(self.city.items()))

	def test_dataclass_to_dict(self):
		expected_city_value = {
			'name':       'New York City',
			'latitude':   40.0,
			'longitude':  -40.5,
			'population': self.city.population,
			'area':       self.city.area
		}
		expected_country_value = {
			'name':       'USA',
			'population': 328000000,
			'cities':     [expected_city_value]
		}

		self.assertDictEqual(expected_city_value, self.city.to_dict())
		self.assertDictEqual(expected_country_value, self.country.to_dict())

	def test_dataclass_from_dict(self):
		data = self.city.to_dict()
		obj = City.from_dict(data)
		self.assertEqual(self.city, obj)
		obj2 = City.from_dict(**data)
		self.assertEqual(self.city, obj2)

	def dataclass_to_yaml(self):
		expected_string = ""
		yaml_string = self.country.to_yaml()

		self.assertEqual(expected_string, yaml_string)

class TestDataclassWrapper(TestDataclassResponseBase, unittest.TestCase):
	def setUp(self):
		population = [(1970, 7894862), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
			(2017, 8660000)]
		self.city = CityWrapped(
			name = 'New York City',
			latitude = 40.0,
			longitude = -40.5,
			population = population,
			area = {
				'total': 1213.37,
				'land':  783.84,
				'water': 429.53,
				'metro': 2342
			}
		)
		self.country = CountryWrapped(
			name = 'USA',
			population = 328000000,
			cities = [self.city]
		)

	def test_dataclass_validation(self):
		data = self.city.to_dict()
		data['area']['moon'] = 'not valid'
		with self.assertRaises(ValueError):
			CityWrapped(**data)

	def test_dataclass_from_dict(self):
		data = self.city.to_dict()
		obj = self.city.from_dict(data)
		self.assertEqual(self.city, obj)
# obj2 = self.city.from_dict().from_dict(**data)
# self.assertEqual(self.city, obj2)


class TestWrappedVsInherited(unittest.TestCase):
	def setUp(self):
		population = [(1970, 7894862), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
			(2017, 8660000)]
		area = {
			'total': 1213.37,
			'land':  783.84,
			'water': 429.53,
			'metro': 34490
		}
		self.basic_city = City(
			name = 'New York City',
			latitude = 40.0,
			longitude = -40.5,
			population = population,
			area = area
		)
		self.wrapped_city = CityWrapped(
			name = 'New York City',
			latitude = 40.0,
			longitude = -40.5,
			population = population,
			area = area
		)
		self.basic_country = Country(
			name = 'USA',
			population = 328000000,
			cities = [self.basic_city]
		)
		self.wrapped_city = CountryWrapped(
			name = 'USA',
			population = 328000000,
			cities = [self.wrapped_city]
		)


if __name__ == "__main__":
	unittest.main()
