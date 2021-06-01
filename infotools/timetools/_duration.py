"""
	A version of timetools built on Pendulum. Pendulum has a number of great features, but suffers from the
	same drawbacks as other Date/time modules when creating an object from another object or uncommon format.
	Pendulum also does not offer convienience methods for some datetime representations (ex. ISO durations).
	Ex. pandas.Timestamp is not compatible with pendulum.datetime.
"""

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import pendulum


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
	def parse(cls, value: Any) -> 'Duration':
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
			#result = pendulum.parse(value)
			#result = cls.from_object(result)
			result = cls.from_string(value)
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
	def to_iso2(self)->str:
		iso_string = "P{year:>02}Y{month:>02}M{days:_02}DT{hours:>02}{minutes:>02}M{seconds:>02}"
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
		if not compact:
			string = "P{years:>02}Y{weeks:>02}W{days:>02}DT{hours:>02}H{minutes:>02}M{seconds:>02}S"
			return string.format(**values)

		suffix_map = [
			('years', 'Y'), ('months', 'M'), ('weeks', 'W'), ('days', 'D'),
			('hours', 'H'), ('minutes', 'M'), ('seconds', 'S')
		]
		suffix_map = dict(suffix_map)

		large_keys = ['years','weeks', 'days']
		small_keys = ['hours', 'minutes', 'seconds']
		# Modify the "seconds" value so it has two digits before the decimal point.
		if values["seconds"] <10:
			values["seconds"] = "0"+str(values['seconds'])

		large_values = "P" + "".join(["{0:>02}{1}".format(values[key], suffix_map[key]) for key in large_keys if values[key] != 0])
		small_values = "T" + "".join(["{0:>02}{1}".format(values[key], suffix_map[key]) for key in small_keys if values[key] != 0])

		isostring = large_values + small_values

		if compact:
			if isostring == 'PT' and not compact:  # Duration of 0 seconds
				isostring = 'PT0S'

		if is_negative:
			isostring = '-' + isostring
		return isostring

	def to_timedelta(self) -> datetime.timedelta:
		""" Returns a timedelta equivilant to `self`"""
		return self.as_timedelta()

	def to_standard(self)->str:
		"""
			Returns the duration formatted as HH:MM:SS.SS. Currently only designed for timedeltas less than a day.
		"""
		hours = self.hours
		minutes = self.minutes
		seconds = self.remaining_seconds + (self.microseconds / 1E6)

		result = f"{hours:>02}:{minutes:>02}:{seconds:>05.2f}"
		return result

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
