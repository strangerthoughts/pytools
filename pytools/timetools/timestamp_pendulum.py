"""
	A version of timetools built on Pendulum. Pendulum has a number of great features, but suffers from the
	same drawbacks as other Date/time modules when creating an object from another object or uncommon format.
	Pendulum also does not offer convienience methods for some datetime representations (ex. ISO durations).
	Ex. pandas.Timestamp is not compatible with pendulum.datetime.
"""

import pendulum
from typing import Any


def _attempt_to_get_attribute(obj: Any, key: str, default = 0):
	try:
		value = getattr(obj, key)
	except AttributeError:
		value = default
	return value


class Timestamp(pendulum.DateTime):

	@classmethod
	def from_object(cls, obj: Any) -> 'Timestamp':
		"""
			Attempts to create a pendulum.DateTime object from another datetime object from a
			different module.
		Parameters
		----------
		obj: Any
			Should have .year, .month, and .day methods, but may also have .hour, .minute, .hour, .tz attributes.

		Returns
		-------
		Timestamp
		"""

		year = obj.year
		month = obj.month
		day = obj.day

		hour = _attempt_to_get_attribute(obj, 'hour', 0)
		minute = _attempt_to_get_attribute(obj, 'minute', 0)
		second = _attempt_to_get_attribute(obj, 'second', 0)
		microsecond = _attempt_to_get_attribute(obj, 'microsecond', 0)
		tz = _attempt_to_get_attribute(obj, 'microsecond', 0)

		result = cls.from_values(year, month, day, hour, minute, second, microsecond)

		return result

	@classmethod
	def from_verbal_date(cls, value: str) -> pendulum.DateTime:
		"""
			Parses a date formatted as DD/MM/YY(YY), as is common in the US.
		Parameters
		----------
		value:str

		Returns
		-------
		pendulum.DateTime
		"""
		month, day, year = list(map(int, value.split('/')))

		return cls.from_values(year, month, day)

	@staticmethod
	def from_values(year, month, day, hour = 0, minute = 0, second = 0, microsecond = 0):
		result = pendulum.DateTime(
			year = year,
			month = month,
			day = day,
			hour = hour,
			minute = minute,
			second = second,
			microsecond = microsecond
		)
		return result


if __name__ == "__main__":
	import datetime

	value = "12/28/2017"
	print(Timestamp.from_verbal_date(value))
