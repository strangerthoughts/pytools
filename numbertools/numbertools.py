import datetime
import math
from numbers import Number

import numpy

def getBase(value):
	""" Returns the SI base for a given value """
	value = abs(value)
	if value < 1E-6:
		suffix = 'n'
		
	elif value < 1E-3:
		suffix = 'u'
		
	elif value < 1:
		suffix = 'm'
		
	elif value < 1000:
		suffix = ''

	elif value < 1E6:
		suffix = 'K'
	
	elif value < 1E9:
		suffix = 'M'
	
	elif value < 1E12:
		suffix = 'B'
	
	elif value <1E15:
		suffix = 'T'
	else:
		message = "'{}' does not have a defined base.".format(value)
		raise ValueError(message)
		
	return suffix

def getMultiplier(base):

	if base == 'n':
		multiplier = 1E-9
	elif base == 'u':
		multiplier = 1E-6
	elif base == 'm':
		multiplier = 1E-3
	elif base == '':
		multiplier = 1.0
	elif base == 'K':
		multiplier = 1E3
	elif base == 'M':
		multiplier = 1E6
	elif base == 'B':
		multiplier = 1E9
	elif base == 'T':
		multiplier = 1E12
	else:
		message = "'{}' is not a valid base.".format(base)
		raise ValueError(message)

	return multiplier


def humanReadable(value, base = None, to_string = True):
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
		Returns
		-------
		str, list<str>
			The reformatted number.
	"""
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
		_toString = lambda v,b: '{0:.2f}{1}'.format(v, b) if v != 0.0 else "0.00"
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


def toNumber(value):
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
			converted_number = int(value)
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
			converted_number = math.nan
	return converted_number

def standardDeviation(values):
	""" Returns the standard deviation of a list of values. """
	return numpy.std(values)

if __name__ == "__main__":
	test_value = datetime.datetime(2015, 6, 6)
	test_value = toNumber(test_value)
	print(test_value)
