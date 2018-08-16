__all__ = ['Response', 'datadict']
from typing import *
from dataclasses import dataclass, asdict
from pytools.datatools.dataclass_validation import validate_item
import yaml
import json
from functools import partial, wraps

def coerce_to_safe_value(item:Any, safe = False)->Any:
	if hasattr(item, 'asdict'):
		item = item.asdict()
	elif hasattr(item, 'to_dict'):
		item = item.to_dict()
	elif hasattr(item, 'todict'):
		item = item.todict()
	elif hasattr(item, 'as_dict'):
		item = item.as_dict()
	if safe and not isinstance(item, (list, set, str, int, float, str, dict)):
		item = str(item)
	return item
# noinspection PyAttributeOutsideInit
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

	def to_dict(self, safe = False) -> Dict:
		# incase asdict fails for some reason
		# return {k: self.get(k) for k in self.keys()}
		# use safe = True for compatibility with json and yaml.
		try:
			result = asdict(self)
		except (TypeError, ValueError):
			result = dict()
			for key in self.fields().keys():
				value = self.get(key)
				if isinstance(value, (list,set,tuple)):
					value = [coerce_to_safe_value(i, safe) for i in value]
				result[key] = value
		result = {k:coerce_to_safe_value(v, safe) for k, v in result.items()}
		result['__class__'] = self.__class__.__name__
		return result

	def to_yaml(self) -> str:
		data = self.to_dict(safe = True)
		try:
			yaml_string = yaml.safe_dump(data)
		except (TypeError, ValueError, yaml.YAMLError):
			yaml_string = yaml.safe_dump(json.loads(json.dumps(data)))
		return yaml_string

	def to_json(self)->str:
		data = self.to_dict()
		return json.dumps(data, indent = 2)

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
		# noinspection PyArgumentList
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


def decorator_with_args(decorator_to_enhance):
	"""
	This function is supposed to be used as a decorator.
	It must decorate an other function, that is intended to be used as a decorator.
	Take a cup of coffee.
	It will allow any decorator to accept an arbitrary number of arguments,
	saving you the headache to remember how to do that every time.
	"""

	# We use the same trick we did to pass arguments

	def decorator_maker(*args, **kwargs):
		# We create on the fly a decorator that accepts only a function
		# but keeps the passed arguments from the maker.
		@wraps(decorator_to_enhance)
		def decorator_wrapper(func):
			# We return the result of the original decorator, which, after all,
			# IS JUST AN ORDINARY FUNCTION (which returns a function).
			# Only pitfall: the decorator must have this specific signature or it won’t work:
			return decorator_to_enhance(func, *args, **kwargs)

		return decorator_wrapper

	return decorator_maker


T = TypeVar('T')
S = TypeVar('S', bound = Response)


def _wrap_dataclass(cls: T) -> S:
	intermediate: S = cls
	allowed = ['__getitem__']
	for key in dir(Response):
		if (key.startswith('_') or key in dir(cls)) and key not in allowed: continue
		# noinspection PyCallByClass
		setattr(intermediate, key, object.__getattribute__(Response, key))
	return intermediate


def datadict(dcls: T) -> Callable[..., S]:
	dcls = _wrap_dataclass(dcls)

	@wraps(dcls)
	def wrapper(*args, **kwargs) -> S:
		obj: S = dcls(*args, **kwargs)
		return obj

	return wrapper


if __name__ == "__main__":
	@dataclass
	class TestA:
		def show_a(self):
			pass


	@dataclass
	class TestB:
		def show_b(self):
			pass


	def decorator(cls):
		class Wrapper(cls, TestA):
			pass

		return Wrapper


	@decorator
	class TestC:
		def show_c(self):
			pass


	c = TestC()
	print(c.show_a())




