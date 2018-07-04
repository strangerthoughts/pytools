from typing import *

BUILTIN_TYPES = [int, float, str, list, dict, tuple, set]

def get_typing_origin(item):
	if item in BUILTIN_TYPES:
		return item
	item_name = get_type_name(item)
	if item_name in {'List', 'Dict', 'Tuple', 'Set',}:

		if item_name == 'List':
			origin = list
		elif item_name == 'Dict':
			origin = dict
		elif item_name == 'Tuple':
			origin = tuple
		elif item_name == 'Set':
			origin = set
		else:
			origin = None
	else:
		try:
			origin = item.__origin__
		except AttributeError:
			origin = None
	return origin


class AnyType:
	def __call__(*args, **kwargs):
		return True


def get_subtypes(item: Any) -> Tuple:
	""" extract typing informations from sequences.
		ex. Union[str, float] -> (str, float)
	"""
	try:
		elements = item.__args__
	except AttributeError:
		elements = ()
	return elements


def get_type_name(item) -> str:
	# pprint(dir(item))
	# print("", flush = True)
	string = str(item).replace('typing.', '')
	if '[' in string:
		name = string.split('[')[0]
	else:
		name = string
	return name


def validate_item(item, expected_type) -> bool:
	# TODO: expected type may be a tuple of types dur to get_subtypes.
	if isinstance(expected_type, tuple):
		result = all(validate_item(item, i) for i in expected_type)
	elif expected_type is None or expected_type is type(None):
		result = item is None or item is type(None)
	elif expected_type == AnyType:
		result = True
	elif expected_type in BUILTIN_TYPES:
		result = isinstance(item, expected_type)
	else:
		result = validate_typing_type(item, expected_type)
	return result


def validate_typing_type(item, expected_type):
	name = get_type_name(expected_type)

	#parameters = get_subtypes(expected_type)
	#origin_result = _validate_origin(expected_type)
	origin_result = True
	if name == 'Any':
		result = True
	elif name in {'Dict', 'Mapping', 'DefaultDict', 'MutableMapping'}:
		result = _validate_mapping(item, expected_type)
	elif name in {'List', 'Iterable', 'Set', 'FrozenSet', 'KeysView', 'ValuesView'}:
		result = _validate_iterable(item, expected_type)
	elif name in ['Tuple', 'NamedTuple']:
		result = _validate_tuple(item, expected_type)
	elif name == 'SupportsInt':
		result = _validate_supports(item, int)
	elif name == 'SupportsFloat':
		result = _validate_supports(item, float)
	elif name == 'SupportsAbs':
		result = _validate_supports(item, abs)
	elif name == 'Union':
		result = _validate_union(item, expected_type)
	elif name == 'Optional':
		result = _validate_optional(item, expected_type)
	elif name == 'Callable':
		result = _validate_callable(item, expected_type)
	else:
		result = True

	return result and origin_result


def _validate_optional(item, type_hint) -> bool:
	return _validate_union(item, type_hint)


def _validate_origin(item) -> bool:
	origin = get_typing_origin(item)
	try:
		result = isinstance(item, origin)
	except (TypeError, ValueError):
		result = True
	return result


def _validate_mapping(mapping, type_hint) -> bool:
	parameters = get_subtypes(type_hint)
	if parameters:
		key_type, value_type = parameters
		result = all(validate_item(i, key_type) for i in mapping.keys())
		result = result and all(validate_item(j, value_type) for j in mapping.values())
	else:
		result = True
	return result


def _validate_iterable(seq, type_hint) -> bool:
	parameters = get_subtypes(type_hint)
	element_type = parameters[0] if parameters else AnyType
	result = all(validate_item(i, element_type) for i in seq)
	return result


def _validate_tuple(seq, type_hint) -> bool:
	parameters = get_subtypes(type_hint)
	result = len(seq) == len(parameters)
	result = result and all(validate_item(i, j) for i, j in zip(seq, parameters))
	return result


def _validate_supports(item, supports_hint) -> bool:
	try:
		supports_hint(item)
		result = True
	except (TypeError, ValueError):
		result = False
	return result


def _validate_union(item, union):
	parameters = get_subtypes(union)
	result = any(validate_item(item, i) for i in parameters)
	return result


def _validate_callable(item, callable_hint):
	# TODO make this a little more advanced
	return callable(item)


def validate_dataclass(obj: Any):
	for key, value_type in obj.__annotations__.items():
		value = getattr(obj, key)
		is_valid = validate_item(value, value_type)
		if not is_valid:
			return False
	else:
		return True


if __name__ == "__main__":
	print(validate_item((1,2,3), Tuple[int,int,int]))
