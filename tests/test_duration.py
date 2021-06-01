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
		{'days': 12, 'seconds': 1245, 'microseconds': 123},
	]
)
def test_parse_duration(data, duration):
	result = Duration(data)
	assert result == duration


@pytest.mark.parametrize(
	"value, expected",
	[
		("00:23:17", 1397),
		("23:17", 1397)
	]
)
def test_parse_duration_variable(value, expected: int):
	# `expected` should be the expected number of seconds.
	result = Duration(value)
	assert result.total_seconds() == expected


@pytest.mark.parametrize(
	"value, expected",
	[
		("00:23:17", 1397),
		("23:17", 1397)
	]
)
def test_parse_duration_from_string(value, expected):
	result = Duration.from_string(value)
	assert result.total_seconds() == expected


def test_duration_attributes():
	# PT8H37M8.070428S 31028.070428 31028
	total_seconds = 31029.070428
	obj = Duration(seconds = total_seconds)
	assert obj.to_iso() == "PT8H37M9.070428S"
	assert obj.days == 0
	assert obj.hours == 8
	assert obj.minutes == 37
	assert obj.seconds == 31029  # Done by pendulum to maintain compatibility with datetime.timedelta.
	assert obj.remaining_seconds == 9
	assert obj.microseconds == 70428


@pytest.mark.parametrize(
	"seconds, expected",
	[
		(10, "00:00:10.00"),
		(31029.070428, "08:37:09.07"),
		(3601, "01:00:01.00")
	]
)
def test_to_standard(seconds, expected):
	duration = Duration(seconds = seconds)
	assert duration.to_standard() == expected


@pytest.mark.parametrize(
	"seconds, expected",
	[
		(100, datetime.timedelta(seconds = 100)),
		(24 * 3600 + 7234, datetime.timedelta(seconds = 24 * 3600 + 7234))
	]
)
def test_to_timedelta(seconds, expected):
	duration = Duration(seconds = seconds)
	result = duration.to_timedelta()

	assert isinstance(result, datetime.timedelta)
	assert result == expected


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

@pytest.mark.parametrize(
	"seconds, expected",
	[
		(10, {'days': 0, 'seconds': 10, 'microseconds': 0}),
		(31029.070428, {'days': 0, 'seconds': 31029, 'microseconds': 70428}),
		(86401.0123, {'days': 1, 'seconds': 1, 'microseconds': 12300})
	]
)
def test_to_dict(seconds, expected):
	duration = Duration(seconds = seconds)
	assert duration.to_dict() == expected

def test_to_iso(seconds, expected):
	result = Duration(seconds = seconds).to_iso()
	assert result == expected