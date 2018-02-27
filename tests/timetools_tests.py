from package import timetools
from datetime import datetime, timedelta
import unittest

# list of timestamps formatted as (test_value, answer)


truth = datetime(2018, 2, 27, 3, 39, 40)
truth_date = datetime(truth.year, truth.month, truth.day)


class TestTimestamp(unittest.TestCase):
	def test_iso_date_timestamp(self):
		string = '2018-02-27'
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth.date)

	def test_datetime_timestamp(self):
		string = '2018-02-27T03:39:40'
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth)

	def test_verbal_date(self):
		string = 'Feb 27, 2018'
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth_date)

	def test_datetime_objects(self):
		t = timetools.Timestamp(truth)
		self.assertTrue(t == truth)

	def test_tuple_datetime(self):
		e = (2018, 2, 27, 3, 39, 40)
		t = timetools.Timestamp(e)
		self.assertTrue(t == truth)

	def test_unpacked_dict_datetime(self):
		e = {
			'year':  truth.year,
			'month': truth.month,
			'day':   truth.day
		}

		t = timetools.Timestamp(**e)

		self.assertTrue(t == truth_date)

	def test_packed_dict_datetime(self):
		e = {
			'year':  2018,
			'month': truth.month,
			'day':   truth.day
		}

		t = timetools.Timestamp(e)
		self.assertTrue(t == truth_date)

	def test_generic_date_object(self):
		class Generic:
			def __init__(self):
				self.year = truth.year
				self.month = truth.month
				self.day = truth.day

		generic_object = Generic()
		t = timetools.Timestamp(generic_object)

		self.assertTrue(t == truth_date)

	def test_standard_datetime_string(self):
		string = '2018/2/27'
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth_date)


if __name__ == "__main__":
	unittest.main()
