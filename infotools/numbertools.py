"""
	Convienient methods for converting between numbers and strings and number representations.
"""

import math
from numbers import Number
from fuzzywuzzy import process
from typing import List, Union, SupportsAbs, Any, Sequence
from dataclasses import dataclass, field

NumberType = Union[int, float]
MU = "μ"


@dataclass
class Scale:
	""" Provides an easy method of checking the magnitude of numbers."""
	prefix: str
	suffix: str
	multiplier: float
	alias: List[str] = field(default_factory = list)  # Alternative methods of referring to this multiplier.

	def __post_init__(self):
		self.alias.append(self.prefix)

	def __ge__(self, other):
		return self.multiplier >= other.multiplier

	def __lt__(self, other):
		return self.multiplier < other.multiplier

	def __eq__(self, other):
		return self.multiplier == other


SCALE: List[Scale] = [
	Scale('atto', 'a', 1E-18),
	Scale('femto', 'f', 1E-15),
	Scale('pico', 'p', 1E-12),
	Scale('nano', 'n', 1E-9),
	Scale('micro', 'u', 1E-6, [MU, 'millionths']),
	Scale('milli', 'm', 1E-3, ['thousandths']),
	# Scale('centi', 'c', 1E-2),
	# Scale('deci', 'd', 1E-1),
	Scale('', '', 1, ['unit', 'one']),
	# Scale('deca', 'da', 1E1),
	# Scale('hecto', 'h', 1E2),
	Scale('kilo', 'K', 1E3, ['thousand']),
	Scale('mega', 'M', 1E6, ['million']),
	Scale('giga', 'B', 1E9, ['billion']),
	Scale('tera', 'T', 1E12, ['trillion']),
	Scale('peta', 'P', 1E15, ['quadrillion']),
	Scale('exa', 'E', 1E18, ['quintillion'])
]

SCALE = sorted(SCALE)
REVERSED_SCALE = sorted(SCALE, reverse = True)

def get_scale(value:Union[str,int,float])->Scale:
	""" Returns the Scale object that represents the given value."""

	if isinstance(value, str):
		for scale in SCALE:
			scale_alias, score = process.extractOne(value.lower(), scale.alias)
			if score > 90:
				base = scale.suffix
				break
		else:
			base = None
	else:
		base = get_base(value)

	if base is None:
		message = f"Could not find a `Scale` object for the given value: `{value}`"
		raise ValueError(message)

	return [i for i in SCALE if i.suffix == base][0]

def is_null(number: Any) -> bool:
	""" Checks if a value represents a null value."""
	try:
		result = number is None or math.isnan(float(number))
	except (TypeError, ValueError):
		result = True

	return result


def get_base(value: SupportsAbs) -> str:
	""" Returns the SI base for a given value """

	value = abs(value)
	if value == 0.0 or is_null(value):
		return ''
	for iso_scale in REVERSED_SCALE:
		if value >= iso_scale.multiplier:
			scale = iso_scale
			break
	else:
		message = "'{}' does not have a defined base.".format(value)
		raise ValueError(message)

	base = scale.suffix
	return base


def get_multiplier(base: str) -> float:
	""" Converts a numerical suffix to the corresponding numerical multiplier.
		Ex. 'K' -> 1000, 'u' -> 1E-6
	"""
	if not isinstance(base, str): return math.nan
	if len(base) > 1:
		base = base.lower()
		if base.endswith('s'):
			base = base[:-1]

	for iso_scale in SCALE:
		prefix = iso_scale.prefix
		suffix = iso_scale.suffix
		if base == prefix or base == suffix or base in iso_scale.alias:
			multiplier = iso_scale.multiplier
			break
	else:
		message = "'{}' is not a valid base.".format(base)
		raise ValueError(message)

	return multiplier


def human_readable(value: NumberType, base: str = None, to_string: bool = True, precision: int = 2) -> Union[str, List[str]]:
	""" Converts a number into a more easily-read string.
		Ex. 101000 -> '101T' or (101, 'T')

		Parameters
		----------
		value: number, list<number>
			Any number or list of numbers. If a list is given, all numbers
			will be asigned the same suffix as the lowest number. 
		base: str; default None
			The base to use. Will be generated automatically if not provided 
		to_string: bool; default True
			If True, the number(s) will be automatically converted to a formatted
			string. Otherwise, a tuple will be returned with the reduced number
			as well as the suffix.
		precision: int; default 2
			The number of decimal places to show.

		Returns
		-------
		str, list<str>
			The reformatted number.
	"""
	template = '{0:.' + str(int(precision)) + 'f}{1}'
	_toString = lambda v, b: template.format(v, b) if v != 0.0 else template.format(0, b)

	if not isinstance(value, list):
		value = [value]

	if base is None:
		values = [i for i in value if not math.isnan(i)]
		if len(values) > 0:
			base = get_base(min(values))
		else:
			return 'nan'

	multiplier = get_multiplier(base)

	human_readable_number = [(i / multiplier, base) for i in value]

	if to_string:
		human_readable_number = [_toString(i[0], i[1]) for i in human_readable_number]

	if len(human_readable_number) == 1:
		human_readable_number = human_readable_number[0]

	return human_readable_number


def is_number(value: Union[Any, Sequence[Any]]) -> Union[bool, List[bool]]:
	"""Tests if the value is a number.

		Examples
		--------
		'abc'->False
		123.123 -> True
		'123.123' -> True

	"""
	if isinstance(value, (list, tuple)):
		return [is_number(i) for i in value]
	if isinstance(value, str):
		try:
			float(value)
			value_is_number = True
		except ValueError:
			value_is_number = False
	else:
		value_is_number = isinstance(value, Number)

	return value_is_number


def _convert_string_to_number(value: str, default = math.nan) -> float:
	if '/' in value:
		left, right = value.split('/')
		left = _convert_string_to_number(left)
		right = _convert_string_to_number(right)
		return left / right
	else:
		value = value.replace(',', '')  # Remove thousands separator.
		value = value.strip()
		try:
			value = float(value)
		except:
			value = default
		return value


def to_number(value: Union[Any, Sequence[Any]], default: Any = math.nan) -> Union[NumberType, List[NumberType]]:
	""" Attempts to convert the passed object to a number.
		Returns
		-------
			value: Scalar
				* list,tuple,set -> list of Number
				* int,float -> int, float
				* str -> int, float
				* generic -> float if float() works, else math.nan
	"""
	if isinstance(value, str):
		return _convert_string_to_number(value, default)

	if isinstance(value, (list, tuple, set)):
		return [to_number(i, default) for i in value]

	try:
		converted_number = float(value)
	except (ValueError, TypeError):
		converted_number = default


	if not is_null(converted_number) and math.floor(converted_number) == converted_number:
		converted_number = int(converted_number)

	return converted_number


if __name__ == "__main__":
	print(to_number('123.456'))
	print(to_number('123.000'))
