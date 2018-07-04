__all__ = ['Response']
from pprint import pprint
from typing import *
from dataclasses import dataclass, asdict
from pytools.datatools.dataclass_validation import validate_item, validate_dataclass
import json
import yaml
import schema
from functools import wraps

@dataclass
class Response:
	"""
		Converts any dataclass into a dict-like object with type-checking.
		Adds a .is_valid attribute which is True if all values are of the required type.
		Supports unpacking with '**'
	"""


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
		if not hasattr(self, '_fields'):
			self._fields = self.__annotations__
		return self._fields

	def items(self) -> List[Tuple[str, Any]]:
		return [(k, self.get(k)) for k in self.keys()]

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

	def is_valid(self) -> bool:
		result = True
		for key, value_type in self.fields().items():
			value = self.get(key)
			vstatus = validate_item(value, value_type)
			result = result and vstatus
			if not result:
				is_valid = False
				break
		else:
			is_valid = True


		return is_valid

def wrapper(cls, validate = True):
	if not hasattr(cls, '__getitem__'):
		cls.__getitem__ = Response.__getitem__
	if not hasattr(cls, 'get'):
		cls.get = Response.get
	if not hasattr(cls, 'keys'):
		cls.keys = Response.keys
	if not hasattr(cls, 'fields'):
		cls.fields = Response.fields
	if not hasattr(cls, 'items'):
		cls.items = Response.items
	if not hasattr(cls, 'to_dict'):
		cls.to_dict = Response.to_dict
	if not hasattr(cls, 'is_valid'):
		cls.is_valid = Response.is_valid

	if validate:
		valid = cls.is_valid()
		if not valid:
			raise ValueError
	return cls

def enforce_types(callable):

	def decorate(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			obj = func(*args, **kwargs)
			is_valid = validate_dataclass(obj)
			pprint(obj.fields())
			if not is_valid:
				message = "The dataclass does not match the given schema!"
				raise ValueError(message)
			return obj
		return wrapper

	return decorate(callable)



if __name__ == "__main__":
	@enforce_types
	@dataclass
	class CityMetadata(Response):
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
		(2017, 'abc')
	]

	data = CityMetadata(
		'New York City',
		'USA',
		40.5, -40.5,
		population
	)


