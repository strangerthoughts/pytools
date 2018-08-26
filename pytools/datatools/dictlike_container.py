from pprint import pprint
from typing import Any, Dict, List, Tuple, KeysView
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
	strict = 'silent'  #

	def __post_init__(self):
		self._fields: Dict[str, Any] = self.__annotations__
		pprint(self._fields)
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
		return {k: self.get(k) for k in self.keys()}

	def is_valid(self) -> bool:

		_valid_types = list()
		for key, value_type in self._fields.items():
			value = self.get(key)
			try:
				is_type = isinstance(value, value_type)
			except TypeError:
				# isinstance doesn't work on generics
				is_type = True
			_valid_types.append(is_type)
			if self.strict == 'warning' or self.strict == 'error':
				# message = "Expected type '{}' in field '{}', got '{}' instead ('{}')."
				message = [is_type, key, value_type, value, type(value)]
				message = '\t'.join(message)
				print(message)
		is_valid = all(_valid_types)
		if self.strict == 'error':
			message = "Recieved an invalid response."
			raise ValueError(message)
		return is_valid


def dictlike(cls, strict = 'silent'):
	cls.strict = strict
	cls.__post_init__ = ResponseBase.__post_init__
	cls.__getitem__ = ResponseBase.__getitem__
	cls.get = ResponseBase.get
	cls.keys = ResponseBase.keys
	cls.fields = ResponseBase.fields
	cls.items = ResponseBase.items
	cls.asdict = ResponseBase.asdict
	cls.toDict = ResponseBase.toDict
	cls.isValid = ResponseBase.isValid
	return cls