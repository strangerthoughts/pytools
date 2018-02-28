from pytools import timetools
from datetime import datetime, timedelta
import unittest
import re
# list of timestamps formatted as (test_value, answer)


truth = datetime(2018, 2, 27, 3, 39, 40)
truth_date = datetime(truth.year, truth.month, truth.day)


iso_date_timestring = '2018-02-27'
iso_datetime_string = '2018-02-27T03:39:40'
verbal_date_string = 'Feb 27, 2018'
datetime_tuple = (2018, 2, 27, 3, 39, 40)


class TestTimestamp(unittest.TestCase):
	def test_iso_date_timestamp(self):
		string = iso_date_timestring
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth_date)

	def test_datetime_timestamp(self):
		string = iso_datetime_string
		t = timetools.Timestamp(string)

		self.assertTrue(t == truth)

	def test_verbal_date(self):
		string = verbal_date_string
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth_date)

	def test_datetime_objects(self):
		t = timetools.Timestamp(truth)
		self.assertTrue(t == truth)

	def test_tuple_datetime(self):

		t = timetools.Timestamp(datetime_tuple)
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
			'year':  truth.year,
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

	def test_common_datetime_string(self):
		string = '2018/2/27'
		t = timetools.Timestamp(string)
		self.assertTrue(t == truth_date)

	def test_long_american_date_format(self):
		string = "{}/{}/{}".format(truth.month, truth.day, truth.year)
		t = timetools.Timestamp(string)
		self.assertTrue(t==truth_date)
	def test_short_american_date(self):
		string = "{}/{}/{}".format(truth.month, truth.day, str(truth.year)[-2:])
		t = timetools.Timestamp(string)
		print(t, truth_date)
		self.assertTrue(t==truth_date)
	def test_long_anglo_date(self):
		string = "{}/{}/{}".format(truth.day,truth.month,truth.year)
		t=timetools.Timestamp(string)
		self.assertTrue(t==truth_date)
if __name__ == "__main__":
	unittest.main()
