import pytest

from infotools import numbertools


@pytest.fixture
def scale() -> numbertools._scale.Scale:
	return numbertools.scale


def test_multiply(scale):
	magnitude = scale.get_magnitude_from_prefix('kilo')

	expected = 1300
	result = magnitude * 1.3
	assert result == expected

	expected = -13
	magnitude = scale.get_magnitude_from_alias("unit")
	result = magnitude * -13
	assert result == expected

	magnitude = scale.get_magnitude_from_prefix('milli')
	expected = pytest.approx(3.14159)
	result = 3141.59 * magnitude
	assert result == expected


def test_eq(scale):
	magnitude = scale.get_magnitude_from_alias('kilo')

	assert 1000 == magnitude

	magnitude = scale.get_magnitude_from_alias('milli')
	assert 0.001 == magnitude


def test_greater_than(scale):
	magnitude = scale.get_magnitude_from_alias('giga')

	assert magnitude > 1
	assert magnitude > scale.get_magnitude_from_alias('kilo')
	assert magnitude >= scale.get_magnitude_from_alias('giga')


def test_less_than(scale):
	magnitude = scale.get_magnitude_from_alias('milli')

	assert magnitude < 1
	assert magnitude < scale.get_magnitude_from_alias('kilo')
	assert magnitude <= scale.get_magnitude_from_alias('giga')


def test_float(scale):
	magnitude = scale.get_magnitude_from_alias('femto')
	assert isinstance(float(magnitude), float)

	magnitude = scale.get_magnitude_from_alias('kilo')
	assert isinstance(float(magnitude), float)

	magnitude = scale.get_magnitude_from_alias('nano')
	assert float(magnitude) == 1E-9


def test_get_magnitude_from_value(scale):
	assert scale.get_magnitude_from_value(1234).multiplier == 1000
	assert scale.get_magnitude_from_value(.1).multiplier == .001


def test_get_magnitude_from_alias(scale):
	assert scale.get_magnitude_from_alias('micro').multiplier == 1E-6
	assert scale.get_magnitude_from_alias('thousand').multiplier == 1000


def test_get_magnitude_from_prefix(scale):
	assert scale.get_magnitude_from_prefix('nano').multiplier == 1E-9
	assert scale.get_magnitude_from_prefix('mega').multiplier == 1E6


if __name__ == "__main__":
	pass
