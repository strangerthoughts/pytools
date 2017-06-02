import math
from numbers import Number


def humanReadable(value):

    if value < 1E-6:
        suffix = 'n'
        multiplier = 1E9
    elif value < 1E-3:
        suffix = 'u'
        multiplier = 1E6
    elif value < 1:
        suffix = 'm'
        multiplier = 1E3
    elif value < 1000:
        suffix = ''
        multiplier = 1
    elif value < 1E6:
        suffix = 'K'
        multiplier = 1E-3
    elif value < 1E9:
        suffix = 'M'
        multiplier = 1E-6
    elif value < 1E12:
        suffix = 'B'
        multiplier = 1E-9
    else:
        suffix = 'T'
        multiplier = 1E-12

    string = '{0:.2f}{1}'.format(value*multiplier, suffix)
    return string


def isNumber(value):
    result = isinstance(value, Number)
    return result


def toNumber(value):
    if isinstance(value, (list, tuple, set)):
        converted_number = [toNumber(i) for i in value]
    elif isinstance(value, str):
        if '.' in value:
            converted_number = float(value)
        else:
            converted_number = int(value)
    elif isinstance(value, (int, float)):
        converted_number = value
    else:
        try:
            converted_number = float(value)
        except TypeError:
            converted_number = math.nan
    return converted_number
