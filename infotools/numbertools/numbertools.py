"""
	Convienient methods for converting between numbers and strings and number representations.
"""

import math
from numbers import Number
from fuzzywuzzy import process
from typing import List, Union, SupportsAbs, Any, Sequence, Optional
from dataclasses import dataclass, field

NumberType = Union[int, float]


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
