from pytools.timetools._duration import Duration

import datetime
import pendulum
from dataclasses import dataclass
from unittest import TestCase, main


class DurationTestData(TestCase):

	def setUp(self):
		# 12 days, 0:02:25.000123
		days = 12
		seconds = 1245
		microseconds = 123

		self.days = days
		self.seconds = seconds
		self.microseconds = microseconds
		self.timedelta_object = datetime.timedelta(days = days, seconds = seconds, microseconds = microseconds)

		self.str_iso_duration_data = "P12DT20M45.000123S"


class DurationTest(DurationTestData):
	def setUp(self):
		super().setUp()

		self.key = pendulum.duration(self.days, self.seconds, self.microseconds)

	def test_iso_duration(self):
		result = Duration(self.str_iso_duration_data)
		self.assertEqual(self.key, result)

	def test_from_object(self):
		@dataclass
		class Generic:
			days: int
			seconds: int
			microseconds: int

		generic_obj = Generic(self.days, self.seconds, self.microseconds)
		from_method = Duration.from_object(generic_obj)
		self.assertEqual(self.key, from_method)

		from_init = Duration(generic_obj)
		self.assertEqual(self.key, from_init)

	def test_from_pendulum(self):
		from_obj = pendulum.Duration(self.days, self.seconds, self.microseconds)
		from_method = pendulum.duration(self.days, self.seconds, self.microseconds)

		self.assertEqual(self.key, from_obj)
		self.assertEqual(self.key, from_method)

	def test_from_timedelta(self):
		tdelta = datetime.timedelta(self.days, self.seconds, self.microseconds)

		from_method = Duration.from_timedelta(tdelta)
		from_init = Duration(tdelta)
		self.assertEqual(self.key, from_method)
		self.assertEqual(self.key, from_init)

	def test_from_tuple(self):
		t = (self.days, self.seconds, self.microseconds)
		from_method = Duration.from_tuple(t)
		from_init = Duration(t)
		self.assertEqual(self.key, from_method)
		self.assertEqual(self.key, from_init)

	def test_from_dict(self):
		d = {
			'days':         self.days,
			'seconds':      self.seconds,
			'microseconds': self.microseconds
		}
		from_method1 = Duration.from_dict(**d)
		from_method2 = Duration.from_keys(d)
		from_init1 = Duration(d)
		from_init2 = Duration(**d)

		self.assertEqual(self.key, from_method1)
		self.assertEqual(self.key, from_method2)
		self.assertEqual(self.key, from_init1)
		self.assertEqual(self.key, from_init2)


if __name__ == "__main__":
	main()
