import math
from numbers import Number

from typing import List, Dict, Union, SupportsAbs, Any

SCALE: List[Dict[str, Union[None,str,int,float]]] = [
	{
		'prefix':     'atto',
		'suffix':     'a',
		'string':     None,
		'multiplier': 1E-18
	},
	{
		'prefix':     'femto',
		'suffix':     'f',
		'string':     None,
		'multiplier': 1E-15
	},
	{
		'prefix':     'pico',
		'suffix':     'p',
		'string':     None,
		'multiplier': 1E-12
	},
	{
		'prefix':     'nano',
		'suffix':     'n',
		'string':     None,
		'multiplier': 1E-9
	},
	{
		'prefix':     'micro',
		'suffix':     'u',  # 'μ'
		'string':     'millionth',
		'multiplier': 1E-6
	},
	{
		'prefix':     'milli',
		'suffix':     'm',
		'string':     'thousandth',
		'multiplier': 1E-3
	},
	{
		'prefix':     'centi',
		'suffix':     'c',
		'string':     'hundredth',
		'multiplier': 1E-2
	},
	{
		'prefix':     'deci',
		'suffix':     'd',
		'string':     'tenth',
		'multiplier': .1
	},
	{
		'prefix':     '',
		'suffix':     '',
		'string':     'unit',
		'multiplier': 1
	},
	{
		'prefix':     'deca',
		'suffix':     'da',
		'string':     'ten',
		'multiplier': 10
	},
	{
		'prefix':     'hecto',
		'suffix':     'h',
		'string':     'hundred',
		'multiplier': 100
	},
	{
		'prefix':     'kilo',
		'suffix':     'K',
		'string':     'thousand',
		'multiplier': 1000
	},
	{
		'prefix':     'mega',
		'suffix':     'M',
		'string':     'million',
		'multiplier': 1E6
	},
	{
		'prefix':     'giga',
		'suffix':     'B',
		'string':     'billion',
		'multiplier': 1E9
	},
	{
		'prefix':     'tera',
		'suffix':     'T',
		'string':     'trillion',
		'multiplier': 1E12
	},
	{
		'prefix':     'peta',
		'suffix':     'P',
		'string':     '',
		'multiplier': 1E15
	},
	{
		'prefix':     'exa',
		'suffix':     'E',
		'string':     '',
		'multiplier': 1E18
	}
]

SCALE = sorted(SCALE, key = lambda s: s['multiplier'])
REVERSED_SCALE = sorted(SCALE, key = lambda s: s['multiplier'], reverse = True)

def is_null(number:Any):
	return number is None or math.isnan(number)

def get_base(value:SupportsAbs):
	""" Returns the SI base for a given value """

	value = abs(value)
	if value == 0.0 or is_null(value):
		return ''
	for iso_scale in REVERSED_SCALE:
		if value >= iso_scale['multiplier']:
			scale = iso_scale
			break
	else:
		message = "'{}' does not have a defined base.".format(value)
		raise ValueError(message)

	base = scale['suffix']
	return base

def get_multiplier(base:str):
	""" Converts a numerical suffix to the corresponding numerical multiplier.
		Ex. 'K' -> 1000, 'u' -> 1E-6
	"""
	if not isinstance(base, str): return math.nan
	if len(base) > 1: 
		base = base.lower()
		if base.endswith('s'):
			base = base[:-1]

	for iso_scale in SCALE:
		prefix = iso_scale['prefix']
		suffix = iso_scale['suffix']
		string = iso_scale['string']
		if base == prefix or base == suffix or base == string:
			multiplier = iso_scale['multiplier']
			break
	else:
		message = "'{}' is not a valid base.".format(base)
		raise ValueError(message)

	return multiplier


def human_readable(value, base:str = None, to_string:bool = True, precision:int = 2)->Union[str,List[str]]:
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
	template =  '{0:.' + str(int(precision)) + 'f}{1}'
	_toString = lambda v, b:template.format(v, b) if v != 0.0 else template.format(0, b)

	if not isinstance(value, list):
		value = [value]

	if base is None:
		values = [i for i in value if not math.isnan(i)]
		if len(values) > 0:
			base = get_base(min(values))
		else:
			return 'nan'

	multiplier = get_multiplier(base)

	human_readable_number = [(i/multiplier, base) for i in value]

	if to_string:

		human_readable_number = [_toString(i[0], i[1]) for i in human_readable_number]

	if len(human_readable_number) == 1:
		human_readable_number = human_readable_number[0]

	return human_readable_number


def is_number(value:Union[str,Number])->bool:
	"""Tests if the value is a number.
		Examples
		--------
			'abc'->False
			123.123 -> True
			'123.123' -> True

	"""
	if isinstance(value, str):
		try:
			float(value)
			is_number = True
		except ValueError:
			is_number = False
	else: 
		is_number = isinstance(value, Number)

	return is_number


def to_number(value:Union[str,Number], default:Any = math.nan)->Union[float,int]:
	""" Attempts to convert the passed object to a number.
		Returns
		-------
			value: Scalar
				* list,tuple,set -> list of Number
				* int,float -> int, float
				* str -> int, float
				* datetime.datetime -> float (with units of 'years')
				* generic -> float if float() works, else math.nan
	"""

	if isinstance(value, (list, tuple, set)):
		converted_number = [to_number(i) for i in value]
	else:
		try:
			converted_number = float(value)
		except ValueError:
			converted_number = default
		except TypeError:
			converted_number = default

	if not is_null(converted_number) and math.floor(converted_number) == converted_number:
		converted_number = int(converted_number)

	return converted_number


if __name__ == "__main__":
	print(to_number('123.456'))
	print(to_number('123.000'))
