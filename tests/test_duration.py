from infotools.timetools import Duration

import datetime
import pendulum
from dataclasses import dataclass
import pytest


@pytest.fixture
def duration():
	data = datetime.timedelta(days = 12, seconds = 1245, microseconds = 123)
	return data


@dataclass
class Generic:
	days: int
	seconds: int
	microseconds: int


@pytest.mark.parametrize(
	"data",
	[
		"P12DT20M45.000123S",
		Generic(12, 1245, 123),
		pendulum.Duration(12, 1245, 123),
		datetime.timedelta(12, 1245, 123),
		(12, 1245, 123),
		{'days': 12, 'seconds': 1245, 'microseconds': 123}
	]
)
def test_parse_duration(data, duration):
	result = Duration(data)
	assert result == duration


def test_duration_repr(duration):
	duration = Duration(duration)
	expected = {'days': 12, 'seconds': 1245, 'microseconds': 123}
	assert duration.to_dict() == expected

	expected = {'years': 0, 'weeks': 1, 'days': 5, 'hours': 0, 'minutes': 20, 'seconds': 45.000123}
	assert duration.tolongdict() == expected

	expected = "P1W5DT20M45.000123S"
	assert duration.to_iso() == expected
	expected = "P0Y0M1W5DT0H20M45.000123S"
	assert duration.to_iso(compact = False) == expected

	td = datetime.timedelta(days = 12, seconds = 1245, microseconds = 123)
	assert isinstance(td, datetime.timedelta)
	assert duration.to_timedelta() == td

	assert pytest.approx(duration.total_years(), (12 / 365))
