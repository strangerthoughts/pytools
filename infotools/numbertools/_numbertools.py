"""
	Convienient methods for converting between numbers and strings and number representations.
"""

import math
from numbers import Number
from typing import Any, Iterable, List, Union

# from ._scale import scale
from . import _scale

default_scale = _scale.DecimalScale()

NumberType = Union[int, float]


def _is_null(value) -> bool:
	if value is None or not isinstance(value, (int, float)):
		return True
	return False


def human_readable(value: NumberType, precision: int = 2) -> str:
	""" Converts a number into a more easily-read string.
		Ex. 101000 -> '101T' or (101, 'T')

		Parameters
		----------
		value: number, list<number>
			Any number or list of numbers. If a list is given, all numbers
			will be asigned the same suffix as the lowest number.
		precision: int; default 2
			The number of decimal places to show.

		Returns
		-------
		str, list<str>
			The reformatted number.
	"""
	template = '{0:.' + str(int(precision)) + 'f}{1}'
	magnitude = default_scale.get_magnitude_from_value(value)
	human_readable_number = value / magnitude.multiplier
	string = template.format(human_readable_number, magnitude.suffix)

	return string


def is_number(value: Union[Any, Iterable[Any]]) -> Union[bool, List[bool]]:
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
		except ValueError:
			value = default
		return value


def to_number(value: Union[Any, Iterable[Any]], default: Any = math.nan) -> Union[NumberType, List[NumberType]]:
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

	if not _is_null(converted_number) and math.floor(converted_number) == converted_number:
		converted_number = int(converted_number)

	return converted_number


