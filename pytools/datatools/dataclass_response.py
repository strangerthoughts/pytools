__all__ = ['Response']
from pprint import pprint
from typing import *
from dataclasses import dataclass, asdict
from pytools.datatools.dataclass_validation import validate_item, validate_dataclass
import json
import yaml
import schema
from functools import wraps
from functools import partial


@dataclass
class Response:
	"""
		Converts any dataclass into a dict-like object with type-checking.
		Adds a .is_valid attribute which is True if all values are of the required type.
		Supports unpacking with '**'
	"""

	def __getitem__(self, item: str) -> Any:
		try:
			return getattr(self, item)
		except AttributeError:
			message = "'{}' has no key '{}'".format(self.__class__.__name__, item)
			raise KeyError(message)
		except TypeError:
			message = "'{}' must be a string".format(item)
			raise TypeError(message)

	def __post_init__(self):
		pass

	def get(self, key: Any, default: Any = None) -> Any:
		try:
			value = self[key]
		except (KeyError, TypeError, AttributeError):
			value = default
		return value

	def keys(self) -> KeysView:
		if not hasattr(self, '_keys'):
			self._keys = self.fields().keys()
		return self._keys

	def values(self) -> List[Any]:
		return [self.get(i) for i in self.keys()]

	def fields(self) -> Dict[str, Any]:
		if not hasattr(self, '_fields'):
			self._fields = self.__annotations__
		return self._fields

	def items(self) -> List[Tuple[str, Any]]:
		return [(k, self.get(k)) for k in self.keys()]

	def to_dict(self) -> Dict:
		# incase asdict fails for some reason
		# return {k: self.get(k) for k in self.keys()}
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

	@classmethod
	def from_dict(cls, data = None, **kwargs):
		if data is None:
			data = kwargs
		return cls(**data)


def __wrap_dataclass(cls):
	if not hasattr(cls, '__getitem__'):
		cls.__getitem__ = Response.__getitem__
	if not hasattr(cls, 'get'):
		cls.get = Response.get
	if not hasattr(cls, 'keys'):
		cls.keys = Response.keys
	if not hasattr(cls, 'values'):
		cls.values = Response.values
	if not hasattr(cls, 'fields'):
		cls.fields = Response.fields
	if not hasattr(cls, 'items'):
		cls.items = Response.items
	if not hasattr(cls, 'to_dict'):
		cls.to_dict = Response.to_dict
	if not hasattr(cls, 'is_valid'):
		cls.is_valid = Response.is_valid
	if not hasattr(cls, 'from_dict'):
		setattr(cls, 'from_dict', partial(Response.from_dict, cls = cls))
	return cls


def _wrap_dataclass(cls):
	allowed = ['__getitem__']
	for key in dir(Response):
		if (key.startswith('_') or key in dir(cls)) and key not in allowed: continue
		setattr(cls, key, object.__getattribute__(Response, key))
	return cls


def datadict(validate = False):
	def decorator(dcls):
		"""
		@dataclass
		class DataClass(dcls, Response):
			def __post_init__(self):
				if hasattr(self, '__post_init__'):
					super().__post_init__()
				if validate and not self.is_valid():
					raise ValueError
		return DataClass
		"""
		dcls = _wrap_dataclass(dcls)

		def wrapper(*args, **kwargs):
			obj = dcls(*args, **kwargs)
			if validate and not obj.is_valid():
				raise ValueError
			return obj

		return wrapper

	return decorator


if __name__ == "__main__":
	@datadict()
	@dataclass
	class ABCTest:
		name: str
		abc: int


	a = ABCTest('A', 123)

	for key in dir(a):
		print(key, '\t', getattr(a, key))
