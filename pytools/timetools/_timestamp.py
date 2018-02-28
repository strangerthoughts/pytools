import datetime
import re

from typing import *

# noinspection PyArgumentList
DateDictType = Dict[str, int]
DateTimeTuple = Tuple[int, int, int, int, int, int, int]


class Timestamp(datetime.datetime):
	timestamp_regex = r"""(?:(?P<year>[\d]{4})-(?P<month>[\d]{2})-(?P<day>[\d]{2}))?
						[\sA-Za-z]?
						(?:(?P<hour>[\d]+)[:](?P<minute>[\d]+)[:](?P<second>[\d]+))?"""
	timestamp_regex = re.compile(timestamp_regex, re.VERBOSE)

	verbal_regex = r"""(?P<first>[\dA-Za-z]+)[,\s]*(?P<second>[\dA-Za-z]+)[,\s]*(?P<year>[\d]+)"""
	verbal_regex = re.compile(verbal_regex, re.VERBOSE)

	def __new__(cls, *args, **kwargs):
		value_format = kwargs.get('value_format')
		if len(args) == 1:
			result = cls._parseInput(args[0], value_format)
		elif len(args) != 0:
			result = cls._parseInput(args, value_format)
		else:
			result = kwargs

		if isinstance(result, dict):
			# noinspection PyArgumentList
			return super().__new__(
				cls,
				result['year'], result['month'], result['day'],
				result.get('hour', 0), result.get('minute', 0), result.get('second', 0))
		else:
			# noinspection PyArgumentList
			return super().__new__(cls, *result)

	def __str__(self):
		string = self.toIso(True)
		return string

	def __repr__(self):
		string = "Timestamp('{}')".format(self.toiso())
		return string

	@staticmethod
	def _cleandict(item: Dict[Union[str, bytes], Union[int, str]]) -> Dict[str, int]:

		item = {k: (int(v) if v else 0) for k, v in item.items()}
		year = item.get('year')
		if year:
			if year < 1000:
				if year < 20:
					year += 2000
				else:
					year += 1900
			item['year'] = year
		return item

	@classmethod
	def _parseExcel(cls, value: int) -> Dict[str, int]:
		value += datetime.date(year = 1899, month = 12, day = 30).toordinal()

		xldate, xltime = divmod(value, 1)
		date = datetime.date.fromordinal(int(xldate))
		# ------------------Convert Time------------------
		second = xltime * (3600 * 24)
		second = int(second)
		hour, second = divmod(second, 3600)
		minute, second = divmod(second, 60)

		result = {
			'year':   date.year,
			'month':  date.month,
			'day':    date.day,
			'hour':   hour,
			'minute': minute,
			'second': second
		}
		return result

	# Methods for converting generic datetime objects
	@classmethod
	def _parseGenericObject(cls, value):
		generic_date = cls._parseGenericDateObject(value)
		generic_time = cls._parseGenericTimeObject(value)
		if generic_date is None:
			message = "Invalid Date Object: {}".format(value)
			raise ValueError(message)
		generic_date.update(generic_time)
		return generic_date

	@classmethod
	def _parseGenericDateObject(cls, element):
		try:
			date_values = {
				'year':  element.year,
				'month': element.month,
				'day':   element.day
			}
		except AttributeError:
			date_values = None
		return date_values

	@classmethod
	def _parseGenericTimeObject(cls, element):
		try:
			time_values = {
				'hour':   element.hour,
				'minute': element.minute,
				'second': element.second
			}
		except AttributeError:
			time_values = dict()
		return time_values

	@classmethod
	def _parseInput(cls, value: Any, value_format = Optional[str]) -> Dict[str, int]:
		if isinstance(value, str):
			result = cls._parseDateTimeString(value, value_format)
		elif isinstance(value, (tuple, list)):
			result = cls._parseTuple(value, value_format)
		elif isinstance(value, dict):
			result = cls._parseDict(value)
		else:
			result = cls._parseGenericObject(value)

		result = cls._cleandict(result)

		return result

	@classmethod
	def _parseDict(cls, value):
		return value

	@classmethod
	def _parseDateTimeString(cls, string: str, value_format = Optional[str]) -> Dict[str, int]:
		""" parses a string formatted as any of the common formats.
			Parameters
			----------
			string: str
				The string to parse.
			value_format: str; default None
				The datetime parser to use. defaults to iso.
				* 'american': 'MM/DD/YY' or 'MM/DD/YYYY'
				* 'anglo': 'DD/MM/YY' or 'DD/MM/YYYY'
				* 'iso': 'YYYY/MM/DD' or 'YYYY-MM-DD'

		"""

		result = cls._parseTimestamp(string, value_format)
		if not result['status']:
			result = cls._parseVerbalDate(string)

		return result

	@classmethod
	def _parseTimestamp(cls, string: str, value_type: Optional[str] = None) -> Dict[str, Union[bool, str]]:
		""" Parses any iso timestamp
		Examples
		--------
			'2018-02-27'                    -> ['2018', '02', '27']
			'2018-02-27T20:08:23+00:00'     -> ['2018', '02', '27', '20', '08', '23', '00', '00']
			'2018-02-27T20:08:23Z'          -> ['2018', '02', '27', '20', '08', '23', '']
			'20180227T200823Z'              -> ['20180227', '200823', '']
			'2018-W09'                      -> ['2018', '', '09']
			'2018-W09-2'                    -> ['2018', '', '09', '2']
		"""

		values = re.split('[^\d]', string)

		if not value_type:
			if 'w' in string:
				value_type = 'iso-week'
			elif len(values) >= 6:
				value_type = 'iso'
			else:
				try:
					a = int(values[0])
					b = int(values[1])
					c = int(values[2])
					if a > 31:
						value_type = 'iso'
					elif c > 31:
						if a <13:
							value_type = 'american'
						else:
							value_type = 'europe'
					else:
						if a<13:
							value_type = 'american'
						elif b<13:
							value_type = 'europe'
						else:
							value_type = 'iso'
				except ValueError:
					value_type = None


		if value_type == 'iso-week':
			# is week
			month = hour = minute = second = None
			year, _, week, *day = values
			if len(day) == 1:
				day = day[0]
			else:
				day = None

		elif value_type == 'iso':
			if len(values) < 6:
				year, month, day = values[:3]
				hour = minute = second = None
			else:
				year, month, day, hour, minute, second = values[:6]
			week = None
		elif value_type == 'numeric':
			year, month, day, hour, minute, second = cls._parseTimestampNumerical(values)
			week = None
		elif value_type == 'american':
			month, day, year = values[:3]
			hour = minute = second = week = None
		elif value_type == 'europe':
			day, month, year = values[:3]
			hour = minute = second = week = None
		else:
			year = month = day = hour = minute = second = week = None

		if '+' in string:
			timezone = string.split('+')[-1]
		elif string[-1].isalpha():
			timezone = string[-1]
		else:
			timezone = None

		status = all([year, month, day]) or all([year, week])

		match = {
			'year':     year,
			'month':    month,
			'day':      day,
			'week':     week,
			'hour':     hour,
			'minute':   minute,
			'second':  second,
			'timezone': timezone,
			'status':   status
		}

		return match

	@classmethod
	def _parseTimestampNumerical(cls, values: List[str]) -> Tuple[str, str, str, str, str, str]:
		"""parses timestamps of the form YYYYMMDD"""

		date_values = values[0]
		time_values = values[1]
		index = 4 if len(date_values) > 6 else 2
		year = date_values[:index]
		month = date_values[index:index + 2]
		day = date_values[index + 2:index + 4]
		if time_values:
			hour = time_values[:2]
			minute = time_values[2:4]
			second = time_values[4:]
		else:
			hour = minute = second = None

		return year, month, day, hour, minute, second

	@classmethod
	def _parseTuple(cls, value: Tuple, value_type:str='date') -> Dict[str, int]:
		if len(value) == 3:
			if value_type == 'date':
				year,month,day = value
				hour=minute=second=None
			else:
				year=month=day = None
				hour,minute,second = value
		elif len(value) >= 6:
			year,month,day,hour,minute,second = value[:6]
		else:
			year=month=day=hour=minute=second=None
		datetime_dict = {
			'year': year,
			'month': month,
			'day': day,
			'hour': hour,
			'minute': minute,
			'second': second,
			'status': all([year, month, day]) or all([hour,minute,second])
		}
		return datetime_dict

	@classmethod
	def _parseVerbalDate(cls, value: str) -> Union[Dict[str, int], None]:
		# Parsed dates formatted verbally. Ex. 7 Oct 2015
		# print("Value: ", value)
		# print(cls.verbal_regex.search(value).groups())
		_short_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
		_long_months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
						'august', 'september', 'november', 'december']
		match = cls.verbal_regex.search(value)
		if not match:
			return None
		else:
			match = match.groups()
		_first, _second, _year = match
		if _first.isdigit():
			_day = _first
			_month = _second
		else:
			_day = _second
			_month = _first
		_month = _month.lower()

		if _month in _short_months:
			_months = _short_months
		else:
			_months = _long_months
		_month = _months.index(_month) + 1

		result = {
			'year':   _year,
			'month':  _month,
			'day':    _day,
			'status': all([_year, _month, _day])
		}
		return result

	# Public access methods
	def getDate(self) -> Tuple[int, int, int]:
		return self.year, self.month, self.day

	def getTime(self) -> Tuple[int, int, int, int]:
		return self.hour, self.minute, self.second, self.microsecond

	def toiso(self, compact: bool = True) -> str:
		result = self.isoformat()
		if compact and not any(i != 0 for i in self.getTime()):
			result = result.split('T')[0]
		return result

	def toIso(self, compact: bool = True) -> str:
		# for compatability with the other methods names.
		return self.toiso(compact)

	def fromString(self, string):
		pass

	def fromObject(self, item):
		pass

	def toDict(self) -> Dict[str, int]:

		struct = self.timetuple()

		result = {
			# Regular
			'year':            struct.tm_year,
			'month':           struct.tm_mon,
			'day':             struct.tm_mday,
			'hour':            struct.tm_hour,
			'minute':          struct.tm_min,
			'second':          struct.tm_sec,
			'microsecond':     0,

			'daylightSavings': struct.tm_isdst,
			'ordinalDay':      struct.tm_yday,
			'weekDay':         struct.tm_wday,
			'timezone':        struct.tm_zone

		}
		return result

	def toTuple(self) -> DateTimeTuple:
		result = (
			self.year, self.month, self.day,
			self.hour, self.minute, self.second, self.microsecond
		)
		return result

	def toYear(self) -> float:
		""" Converts the timestamp to a float """

		data = self.toDict()

		year = data['year']

		ordinal_day = data['ordinalDay']
		if ordinal_day >= 364: ordinal_day = 364

		result = year + ((ordinal_day - 1) / 365)

		return result

	def toDatetime(self) -> datetime.datetime:
		return datetime.datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)


if __name__ == "__main__":
	stringa = "2018-11-13"
	stringb = "2018-02-24T19:49:24+00:00"
	stringc = None

	print(Timestamp(stringa))
	print(Timestamp(stringb))
	print(Timestamp(stringc))
	help(Timestamp.toiso)
