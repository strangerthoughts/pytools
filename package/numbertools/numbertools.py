import datetime
import math
from numbers import Number
import numpy


SCALE = [
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

def getBase(value):
	""" Returns the SI base for a given value """

	value = abs(value)
	if value == 0.0 or math.isnan(value):
		return ''
	for iso_scale in REVERSED_SCALE:
		if value > iso_scale['multiplier']:
			scale = iso_scale
			break
	else:
		message = "'{}' does not have a defined base.".format(value)
		raise ValueError(message)

	base = scale['suffix']
	return base

def getMultiplier(base):
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


def humanReadable(value, base = None, to_string = True, precision = 2):
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
			base = getBase(min(values))
		else:
			return 'nan'

	multiplier = getMultiplier(base)

	result = [(i/multiplier, base) for i in value]

	if to_string:

		result = [_toString(i[0], i[1]) for i in result]

	if len(result) == 1:
		result = result[0]

	return result


def isNumber(value):
	if isinstance(value, str):
		result = value.isdigit()
	else: 
		result = isinstance(value, Number)

	return result


def toNumber(value, default = math.nan):
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
		converted_number = [toNumber(i) for i in value]
	elif isinstance(value, str):
		if '.' in value:
			converted_number = float(value)
		else:
			try:
				converted_number = int(value)
			except:
				converted_number = default
	elif isinstance(value, (int, float)):
		converted_number = value
	elif isinstance(value, datetime.datetime):
		year = value.year
		month = value.month
		day = value.day
		converted_number = year + (month/12) + (day/365)
	else:
		try:
			converted_number = float(value)
		except TypeError:
			converted_number = default
	return converted_number

def standardDeviation(values):
	array = numpy.array(values)
	return array.std()

if __name__ == "__main__":
	test_value = 12345
	test_value = -123456


	result = humanReadable(test_value, precision = 2)
	print(result)