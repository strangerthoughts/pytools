from pytools.datatools import datadict
from dataclasses import dataclass
from typing import List, Tuple

from pprint import pprint
@datadict
@dataclass
class City:
	name: str
	population: List[Tuple[int, int]]


@datadict
@dataclass
class Country:
	name: str
	cities: List[City]

if __name__ == "__main__":
	city_a = City(
		name = 'New York City',
		population = [(1970, 7894862), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
			(2017, 8660000)]
	)

	city_b = City(
		name = 'Los Angeles',
		population = [(1970, 2811801), (1980, 2968528), (1990, 3485398), (2000, 3694820), (2010, 3792621),
			(2017, 3999759)]
	)

	country = Country(
		'USA',
		[city_a, city_b]
	)
	print(country)
	pprint(country.to_dict())
	print()
	print(country.to_json())
	print()
	print(country.to_yaml())
