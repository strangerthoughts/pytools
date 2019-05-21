"""
	Suite of tests for numbertools
"""

import pytest
from infotools import numbertools


@pytest.mark.parametrize(
	"number,expected",
	[
		(1000, 'K'),
		(1E-9, 'n'),
		(0, ''),
		(1234, 'K'),
		(123E-5, 'm'),
		(3.14159, '')
	]
)
def test_get_base(number, expected):
	assert expected == numbertools.get_base(number)


@pytest.mark.parametrize("string,expected",
	[
		('n', 1E-9),
		('K', 1000),
		('T', 1E12),
		('', 1)
	]
)
def test_get_multiplier(string, expected):
	assert expected == numbertools.get_multiplier(string)


@pytest.mark.parametrize("value,expected",
	[
		(123.456, True),
		('123.456', True),
		('abc', False),
		('12.345.678', False),
		("1E6", True),
		([123, "456.f", "789.0"], [True, False, True])
	])
def test_is_number(value, expected):
	assert expected == numbertools.is_number(value)


@pytest.mark.parametrize("number,precision,expected",
	[
		(1234.123, 6, '1.234123K'),
		(12.5E-6, 1, '12.5u'),
		(111222333444555, 12, '111.222333444555T')
	]
)
def test_human_readable(number, precision, expected):
	assert numbertools.human_readable(number, precision = precision) == expected

@pytest.mark.parametrize(
	"value,expected",
	[
		("5.4", 5.4),
		('asfkjnlmlqwe', None),
		('7.8/10 ', 0.78)
	]
)
def test_convert_string_to_number(value, expected):
	result = numbertools._convert_string_to_number(value, default = None)

	assert result == expected
@pytest.mark.parametrize(
	"value,expected",
	[
		("5.4", 5.4),
		('asfkjnlmlqwe', None),
		('7.8/10 ', 0.78),
		(['7.8/10', '99'], [0.78, 99])
	]
)

def test_to_number(value,expected):
	result = numbertools.to_number(value, None)

	assert result == expected

