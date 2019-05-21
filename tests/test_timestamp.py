"""
	A suite of tests to ensure timetools.Timestamp is operating properly.
"""
from infotools import timetools
import datetime
import pandas
import pytest


@pytest.fixture
def timestamp():
	key = "2019-05-06 00:14:26.246155"
	ts = datetime.datetime(2019, 5, 6, 0, 14, 26, 246155)
	return ts


@pytest.mark.parametrize(
	"data",
	[
		"05/06/2019",
		{'year': 2019, 'month': 5, 'day': 6},
		{'year': 2019, 'month': 5, 'day': 6, 'hour': 0, 'minute': 14, 'second': 26, 'microsecond': 246155},
		(2019, 5, 6),
		(2019, 5, 6, 0, 14, 26, 246155),
		"may 6, 2019",
		"06 may 2019",
		pandas.Timestamp(year = 2019, month = 5, day = 6)

	]
)
def test_parse_timestamp_date(data, timestamp):
	result = timetools.Timestamp(data).date()

	assert result == timestamp.date()


@pytest.mark.parametrize("data",
	[
		{'year': 2019, 'month': 5, 'day': 6, 'hour': 0, 'minute': 14, 'second': 26, 'microsecond': 246155},
		(2019, 5, 6, 0, 14, 26, 246155),
		datetime.datetime(2019, 5, 6, 0, 14, 26, 246155),

	]
)
def test_parse_timestamp_datetime(data, timestamp):
	result = timetools.Timestamp(data)
	assert result == timestamp

def test_to_float():
	ts = timetools.Timestamp((2019,2,13))
	expected = 2019 + (44/365)
	assert float(ts) == expected