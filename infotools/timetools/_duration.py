"""
	A version of timetools built on Pendulum. Pendulum has a number of great features, but suffers from the
	same drawbacks as other Date/time modules when creating an object from another object or uncommon format.
	Pendulum also does not offer convienience methods for some datetime representations (ex. ISO durations).
	Ex. pandas.Timestamp is not compatible with pendulum.datetime.
"""

import pendulum
import datetime
from typing import Any, Tuple, Dict
from dataclasses import dataclass


@dataclass
class TimedeltaInformation:
	"""Helps keep track of data being passed around."""
	days: int
	seconds: int
	microseconds: int

	def to_dict(self):
		""" Converts `self` to a dict"""
		data = {
			'days':         self.days,
			'seconds':      self.seconds,
			'microseconds': self.microseconds
		}
		return data


class Duration(pendulum.Duration):
	"""
		A drop-in replacement for datetime and Pendulum. Contains a number or
		useful methods for time timedelta representations.
	"""
	def __new__(cls, value = None, **kwargs):
		"""
			Keyword Arguments
			-----------------
			All arguments are optional and default to 0.
			Arguments may be integers or floats, and may be positive or negative.
				days:         number; default 0
				seconds:      number; default 0
				microseconds: number; default 0
				milliseconds: number; default 0
				minutes:      number; default 0
				hours:        number; default 0
				weeks:        number; default 0
		"""
		if value is not None:
			return cls.parse(value)

		return super().__new__(cls, **kwargs)

	# self.duration = pendulum.duration(**duration_keys)

	def __str__(self):
		return self.to_iso()

	def __repr__(self):
		repr_string = "Duration('{}')".format(self.to_iso())
		return repr_string

	@classmethod
	def parse(cls, value: Any) -> TimedeltaInformation:
		"""
			Attempts to parse/coerce any object into a timedelta.
			The given element will be parsed by pendulum.parse, when possible.
		Parameters
		----------
		value

		Returns
		-------

		"""
		if isinstance(value, str):
			result = pendulum.parse(value)
			result = cls.from_object(result)
		elif isinstance(value, dict):
			result = cls.from_keys(value)

		elif isinstance(value, (list, tuple)):
			result = cls.from_tuple(value)
		else:
			result = cls.from_object(value)

		return result

	@classmethod
	def from_dict(cls, **keys) -> 'Duration':
		""" initializes a `Duration` object from a dictionary using `**` notation."""
		return cls(**keys)

	@classmethod
	def from_keys(cls, keys: Dict[str, int]) -> 'Duration':
		""" initializes a `Duration` object from a dictionary."""
		return cls(**keys)

	@classmethod
	def from_string(cls, string: str) -> 'Duration':
		"""
			Parses a string. Defaults to pendulum.parse
		Parameters
		----------
		string: str

		Returns
		-------
		Duration
		"""
		if ':' in string:
			times = string.split(':')
			if len(times) == 1:
				hour = minute = 0
				second = float(times[0])
			elif len(times) == 2:
				hour = 0
				minute, second = map(float, times)  # use float to preserve milliseconds
			else:
				hour, minute, second = map(float, times)
			return cls(hours = hour, minutes = minute, seconds = second)
		else:
			result = pendulum.parse(string)
			return cls.from_object(result)

	@classmethod
	def from_object(cls, obj: Any) -> 'Duration':
		"""
			Attempts to convert a generic object to a timedelta Duration.
		Parameters
		----------
		obj: Any

		Returns
		-------
		Duration
		"""
		if hasattr(obj, 'as_timedelta'):
			obj = obj.as_timedelta()  # Converts pendulum.Duration to a timedelta.
		if isinstance(obj, datetime.timedelta) or hasattr(obj, 'total_seconds'):
			seconds = obj.total_seconds()
			days = 0
			microseconds = 0
		elif isinstance(obj, pendulum.Duration):
			seconds = obj.in_seconds()
			days = 0
			microseconds = 0
		else:
			try:
				days = obj.days
				seconds = obj.seconds
				microseconds = obj.microseconds
			except AttributeError:
				message = "Object '{}' with type '{}' cannot be coerced to a time duration.".format(obj, type(obj))
				raise AttributeError(message)

		result = {
			'days':         days,
			'seconds':      seconds,
			'microseconds': microseconds
		}
		return cls.from_dict(**result)

	@classmethod
	def from_timedelta(cls, obj: datetime.timedelta) -> 'Duration':
		""" Wrapper around .from_object that allows explicit initialization from a timedelta."""
		return cls.from_object(obj)

	@classmethod
	def from_tuple(cls, value: Tuple) -> 'Duration':
		"""
			Attempts to construct a timedelta form an iterable.
		Parameters
		----------
		value: Tuple[int,int,int]
			The value must consist of three parts: days, seconds, microseconds.

		Returns
		-------
		Duration
		"""
		if len(value) != 3:
			message = f"The value passed to Duration.from_tuple must contain exactly 3 values (recieved {value})."
			raise ValueError(message)
		keys = ['days', 'seconds', 'microseconds']
		timedelta_keys = dict(zip(keys, value))
		return cls.from_dict(**timedelta_keys)

	def to_dict(self) -> Dict[str, int]:
		""" Returns a dictionary that can be used to instantiate another timedelta or Duration object. """
		result = {
			'days':         self.days,
			'seconds':      self.seconds,
			'microseconds': self.microseconds
		}
		return result

	def tolongdict(self) -> Dict[str, int]:
		""" Returns a dictionary with more human readable date and time keys. """

		is_negative = self.total_seconds() < 0
		if is_negative:
			original = abs(self)
			original = {
				'days':         original.days,
				'seconds':      original.seconds,
				'microseconds': original.microseconds
			}
		else:
			original = self.to_dict()
		longdict = dict()
		# Get date values
		days = original['days']
		longdict['years'], days = divmod(days, 365)
		longdict['weeks'], longdict['days'] = divmod(days, 7)

		# Get time values
		seconds = original['seconds']
		longdict['hours'], seconds = divmod(seconds, 3600)
		longdict['minutes'], longdict['seconds'] = divmod(seconds, 60)
		longdict['seconds'] += original['microseconds'] / 1000000

		# Since timedelta objects subtract positive numbers from the largest unit for negative timestamps, need to convert back,

		return longdict

	def to_iso(self, compact: bool = True) -> str:
		""" Converts the timedelta to an ISO Duration string. By default,
			weeks are used instead of months, so the original duration string
			used to create to Duration object may differ (but will be equivilant to)
			the output of this method.
			Parameters
			----------
				compact: bool; default False
					Whether to omit emty fields.
		"""
		is_negative = self.total_seconds() < 0
		values = self.tolongdict()
		datetime_map = [
			'P', ('years', 'Y'), ('months', 'M'), ('weeks', 'W'), ('days', 'D'),
			'T', ('hours', 'H'), ('minutes', 'M'), ('seconds', 'S')]
		datetime_values = list()

		for key in datetime_map:
			if isinstance(key, tuple):
				element = (values.get(key[0], 0), key[1])
				if compact and element[0] == 0: continue
				datetime_values.append(element)
			else:
				datetime_values.append(("", key))

		isostring = "".join("{}{}".format(i, j) for i, j in datetime_values)

		if compact:
			if isostring == 'PT' and not compact:  # Duration of 0 seconds
				isostring = 'PT0S'
		# isostring[0] == 'P' and isostring[1] == 'T': isostring = isostring[1:]
		# elif isostring[-1] == 'T': isostring = isostring[:1]

		if is_negative:
			isostring = '-' + isostring
		return isostring

	def to_timedelta(self) -> datetime.timedelta:
		""" Returns a timedelta equivilant to `self`"""
		return self.as_timedelta()

	def total_years(self) -> float:
		"""
			Returns the total number of years contained in the duration as a float.
		Returns
		-------

		"""
		return self.total_days() / 365

	def to_json(self) -> str:
		""" Returns a json-safe representation of `self`"""
		return str(self)

	def to_yaml(self) -> str:
		""" Returns a yaml representation of `self`"""
		return self.to_json()


if __name__ == "__main__":
	D = Duration("P13DT5S")
	print(repr(D))
