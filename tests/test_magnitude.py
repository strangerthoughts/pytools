import pytest
from infotools import numbertools


@pytest.fixture
def scale() -> numbertools.Scale:
	return numbertools.Scale()


@pytest.mark.parametrize(
	"value, expected",
	[
		(123, ""),
		(.123, "milli"),
		(1234567890, "giga")
	]
)
def test_get_magnitude_from_value(scale, value, expected):
	result = scale.get_magnitude_from_value(value)
	assert result.prefix == expected

@pytest.mark.parametrize(
	"value, expected",
	[]
)
def test_get_magnitude_from_prefix(scale, value, expected):
	pass
