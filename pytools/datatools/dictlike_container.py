__all__ = ['ResponseBase']
from pprint import pprint
from typing import *
from dataclasses import dataclass, asdict
import json
import yaml
import schema

@dataclass
class ResponseBase:
	"""
		Converts any dataclass into a dict-like object with type-checking.
		Adds a .is_valid attribute which is True if all values are of the required type.
		Supports unpacking with '**'
	"""
	# Determines how to handle incorrect arguments.
	# 'silent' - silent, do nothing
	# 'warning' - print a warning message
	# 'error' - raise an error.
	strict = 'warning'  #

	def __post_init__(self):
		self._fields: Dict[str, Any] = self.__annotations__

		self.is_valid: bool = self.isValid()

	def __getitem__(self, item: str) -> Any:
		if item not in self.keys():
			message = "'{}' does not exist in the keys.".format(item)
			raise KeyError(message)
		return getattr(self, item)

	def get(self, key: Any, default: Any = None) -> Any:
		try:
			value = self[key]
		except KeyError:
			value = default
		return value

	def keys(self) -> KeysView:
		return self._fields.keys()

	def fields(self) -> Dict[str, Any]:
		return self._fields

	def items(self) -> List[Tuple[str, Any]]:
		return [(k, self.get(k)) for k in self.keys()]

	def asdict(self) -> Dict:
		return self.toDict()

	def to_dict(self) -> Dict:
		# incase asdict fails for some reason
		#return {k: self.get(k) for k in self.keys()}
		try:
			result = asdict(self)
		except:
			result = dict()
			for key in self.fields().keys():
				value = self.get(key)
				if hasattr(value, 'asdict'): value = value.asdict()
				elif hasattr(value, 'to_dict'): value = value.to_dict()
				elif hasattr(value, 'todict'): value = value.todict()
				elif hasattr(value, 'as_dict'): value = value.as_dict()
				result[key] = value
		return result

	def isValid(self) -> bool:
		_valid_types = list()
		for key, value_type in self._fields.items():
			value = self.get(key)
			try:
				is_type = isinstance(value, value_type)
			except TypeError:
				# isinstance doesn't work on generics
				is_type = True
			_valid_types.append(is_type)
			if not is_type and (self.strict == 'warning' or self.strict == 'error'):
				# message = "Expected type '{}' in field '{}', got '{}' instead ('{}')."
				message = [is_type, key, value_type, value, type(value)]
				message = '\t'.join(map(str,message))
				print(message)
		is_valid = all(_valid_types)
		if self.strict == 'error':
			message = "Recieved an invalid response."
			raise ValueError(message)
		return is_valid


def extract_schema(annotations: Dict[str, Any]):
	from schema import Schema, And, Optional
	pprint(annotations)
	print()
	converted_schema = dict()
	for item_key, item_type in annotations.items():
		if item_type in {str, int, float, bool}:
			converted_schema[item_key] = item_type
		else:
			if item_type is Union:
				converted_schema[item_key] = item_type

	pprint(converted_schema)

def validate_type(item, expected_type):
	type_name = get_n

if __name__ == "__main__":
	@dataclass
	class CityMetadata(ResponseBase):
		name: str
		country: str
		latitude: float
		longitude: float
		population_history: List[Tuple[int, int]]


	population = [
		(1860, 1174778),
		(1870, 1478103),
		(1880, 1911698),
		(1890, 2507414),
		(1900, 3437202),
		(1910, 4766883),
		(1920, 5620048),
		(1930, 6930446),
		(1940, 7454995),
		(1950, 7891957),
		(1960, 7781984),
		(1970, 7894862),
		(1980, 7071639),
		(1990, 7322564),
		(2000, 8008278),
		(2010, 8175133),
		(2017, 8622698)
	]

	data = CityMetadata(
		'New York City',
		'USA',
		40.5, -40.5,
		population
	)

	print(data.is_valid)
