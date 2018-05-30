"""
	A version of timetools built on Pendulum. Pendulum has a number of great features, but suffers from the
	same drawbacks as other Date/time modules when creating an object from another object or uncommon format.
	Pendulum also does not offer convienience methods for some datetime representations (ex. ISO durations).
	Ex. pandas.Timestamp is not compatible with pendulum.datetime.
"""

import pendulum
from typing import Any, Dict, Tuple, Union

STuple = Tuple[int,...]
TTuple = Tuple[int, int, int]


def _attempt_to_get_attribute(obj: Any, key: str, default = 0):
	try:
		attribute = getattr(obj, key)
	except AttributeError:
		attribute = default
	return attribute


class Timestamp(pendulum.DateTime):
	def __new__(cls, *args, **kwargs):
		if len(args) == 1:
			value = args[0]
		elif len(args) > 1:
			return cls.from_values(*args)
		else:
			value = None
		if value is not None:
			return cls.parse(value)
		result = super().__new__(cls, **kwargs)

		return result
	@classmethod
	def parse(cls, value: Any) -> 'Timestamp':
		if isinstance(value, str):
			result = cls.from_string(value)
		elif isinstance(value, (list, tuple)):
			result = cls.from_tuple(value)
		elif isinstance(value, dict):
			result = cls.from_keys(value)
		else:
			result = cls.from_object(value)
		return result

	@classmethod
	def from_dict(cls, **kwargs) -> 'Timestamp':
		return cls(**kwargs)

	@classmethod
	def from_keys(cls, keys: Dict[str, int]) -> 'Timestamp':
		return cls.from_dict(**keys)
	@classmethod
	def from_tuple(cls, value:Union[STuple, TTuple])->'Timestamp':
		if len(value) == 3:
			year, month, day = value
			hour, minute, second = 0, 0, 0
			other = []
		else:
			year, month, day, hour, minute, second, *other = value

		data = {
			'year': year,
			'month': month,
			'day': day,
			'hour': hour,
			'minute': minute,
			'second': second
		}
		if len(other) > 0:
			data['microsecond'] = other[0]
		else:
			data['microsecond'] = 0
		return cls.from_dict(**data)

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
		if ' ' in value:
			dates, times = value.split(' ')
		elif 'T' in value:
			dates, times = value.split('T')
		else:
			dates = value
			times = ""

		month, day, year = list(map(int, dates.split('/')))

		if times:
			hour, minute, second, *other = list(map(int, times.split(':')))
		else:
			hour, minute, second = 0, 0, 0

		keys = {
			'year':   year,
			'month':  month,
			'day':    day,
			'hour':   hour,
			'minute': minute,
			'second': second
		}

		return cls.from_dict(**keys)

	@classmethod
	def from_string(cls, value: str) -> 'Timestamp':
		try:
			obj = pendulum.parse(value)
		except:
			obj = cls.from_verbal_date(value)
		return cls.from_object(obj)

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
	pass
