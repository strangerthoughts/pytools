"""
	Suite of tests for numbertools
"""

import random

import hypothesis
import hypothesis.strategies as st
import pytest

from infotools import numbertools


@pytest.fixture
def decimal() -> numbertools.DecimalScale:
	return numbertools.DecimalScale()


@pytest.fixture
def binary() -> numbertools.BinaryScale:
	return numbertools.BinaryScale()


@st.composite
def numerical_values(draw):
	x = draw(st.integers())
	y = draw(st.floats())
	z = random.randint(0,1)
	return x if z else y


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

@hypothesis.given(st.floats())
def test_is_number_hypothesis(value):

	assert numbertools.is_number(value)

@pytest.mark.parametrize("number,precision,expected",
	[
		(1234.123, 6, '1.234123K'),
		(12.5E-6, 1, '12.5u'),
		(111222333444555, 12, '111.222333444555T'),
		(-1234.123, 6, '-1.234123K'),
		(-500_000_000_000.0, 2, "-500.00B"),
		(-500_000_000_000.0, 0, "-500B"),
		(0.0, 0, "0"),
		(0.0, 2, "0.00")
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
	result = numbertools.to_number(value, default = None)

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
def test_to_number(value, expected):
	result = numbertools.to_number(value, None)

	assert result == expected


@pytest.mark.parametrize(
	"value",
	[
		"kilo", "micro", "milli", "femto"
	]
)
def test_get_magnitude_from_prefix(value):
	result = numbertools.DecimalScale().get_magnitude_from_prefix(value)
	assert result.prefix == value

@pytest.mark.parametrize(
	"system", [numbertools.DecimalScale(), numbertools.BinaryScale()]
)
def test_get_unit_magnitude(system):
	assert system.get_unit_magnitude() == system.get_magnitude_from_alias('unit')

@pytest.mark.parametrize(
	"value,expected",
	[
		(1234, 'kilo'),
		(1E-4, 'micro'),
		(0.123, 'milli'),
		(0.0, "")
	]
)
def test_get_magnitude_from_value(decimal, value, expected):
	result = decimal.get_magnitude_from_value(value)
	assert result.prefix == expected


@pytest.mark.parametrize(
	"value,expected",
	[
		('billion', 'giga'),
		('Millions', 'mega')
	]
)
def test_get_magnitude_from_alias(decimal, value, expected):
	result = decimal.get_magnitude_from_alias(value)

	assert result.prefix == expected

