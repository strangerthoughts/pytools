
import datetime
import re

from pprint import pprint
# noinspection PyArgumentList
class Timestamp(datetime.datetime):
	timestamp_regex = r"""(?:(?P<year>[\d]{4})-(?P<month>[\d]{2})-(?P<day>[\d]{2}))?
						[\sA-Za-z]?
						(?:(?P<hour>[\d]+)[:](?P<minute>[\d]+)[:](?P<second>[\d]+))?"""
	timestamp_regex = re.compile(timestamp_regex, re.VERBOSE)

	def __new__(cls, *args, **kwargs):
		if len(args) == 1:
			result = cls._parseInput(args[0])
		elif len(args) == 3:
			result = {'year': args[0], 'month': args[1], 'day': args[2]}
			result.update(kwargs)
		elif len(args) != 0:
			result = args
		else:
			result = kwargs
		if isinstance(result, dict):
			return super().__new__(
				cls,
				result['year'], result['month'], result['day'],
				result.get('hour', 0), result.get('minute', 0), result.get('second', 0))
		else:
			return super().__new__(cls, *result)

	def __str__(self):
		string = self.toIso(True)
		return string
	@staticmethod
	def _cleandict(item):
		item = {k: (int(v) if v else 0) for k, v in item.items()}
		return item
	
	@classmethod
	def _parseExcel(cls, value):
		value += datetime.date(year = 1899, month = 12, day = 30).toordinal()
			
		xldate, xltime = divmod(value, 1)
		date = datetime.date.fromordinal(int(xldate))
		# ------------------Convert Time------------------
		second = xltime * (3600 * 24)
		second = int(second)
		hour, second = divmod(second, 3600)
		minute, second = divmod(second, 60)
		
		result = {
			'year': date.year,
			'month': date.month,
			'day': date.day,
			'hour': hour,
			'minute': minute,
			'second': second
		}
		return result

	@classmethod
	def _parseGenericObject(cls, value):
		generic_date = cls._parseGenericDateObject(value)
		generic_time = cls._parseGenericTimeObject(value)
		if generic_date is None:
			message = "Invalid Date: {}".format(value)
			raise ValueError(message)
		generic_date.update(generic_time)
		return generic_date

	@classmethod
	def _parseGenericDateObject(cls, element):
		try:
			date_values = {
				'year': element.year,
				'month': element.month,
				'day': element.day
			}
		except AttributeError:
			date_values = None
		return date_values

	@classmethod
	def _parseGenericTimeObject(cls, element):
		try:
			time_values = {
				'hour': element.hour,
				'minute': element.minute,
				'second': element.second
			}
		except AttributeError:
			time_values = dict()
		return time_values

	@classmethod
	def _parseInput(cls, value):
		if isinstance(value, str):
			if any(not c.isdigit() for c in value):
				result = cls._parseTimestamp(value)
			else:
				result = cls._parseNumericString(value)
		elif isinstance(value, (tuple, list)):
			result = cls._parseTuple(value)
		else:
			result = cls._parseGenericObject(value)

		return result

	@classmethod
	def _parseDateTimeString(cls, string):
		""" parses a string formatted as a generic YY/MM/DD string. """
		if '-' in string and ':' in string:
			result = cls._parseTimestamp(string)
		elif ' ' in string:
			result = cls._parseVerbalDate(string)
		else:
			result = cls._parseNumericString(string)
		return result

	@classmethod
	def _parseNumericString(cls, string):
		""" Parses a date formatted as YY[YY]MMDD. """
		string, day = string[:-2], string[-2:]
		year, month = string[:-2], string[-2:]

		year = int(year)
		if year < 20: year += 2000
		else: year += 1900

		result = {
			'year': int(year),
			'month': int(month),
			'day': int(day),
			'hour': 0,
			'minute': 0,
			'second': 0
		}
		return result

	@classmethod
	def _parseTimestamp(cls, string):
		""" Parses a date and/or time formated as YYYY-MM-DDThh:mm:ss"""
		match = cls.timestamp_regex.search(string).groupdict()
		match = cls._cleandict(match)
		return match

	@classmethod
	def _parseTuple(cls, value):
		keys = ('year', 'month', 'day', 'hour', 'minute', 'second')
		result = dict(zip(keys, value))
		return result

	@classmethod
	def _parseVerbalDate(cls, value):
		# Parsed dates formatted verbally. Ex. 7 Oct 2015
		_short_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'sep', 'oct', 'nov', 'dec']
		_long_months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
			'august', 'september', 'november', 'december']
		_day, _month, _year = value.split(' ')
		_month = _month.to_lower()
		if _month in _short_months:
			_months = _short_months
		else:
			_months = _long_months
		_month = _months.index(_month) + 1

		result = {
			'year': int(_year),
			'month': int(_month),
			'day': int(_day)
		}
		return result

	def getTime(self):
		return self.hour, self.minute, self.second, self.microsecond

	def toiso(self, compact = True):
		result = self.isoformat()
		if compact and not any(i != 0 for i in self.getTime()):
			result = result.split('T')[0]
		return result

	def toIso(self, compact = True):
		# for compatability with the other methods names.
		return self.toiso(compact)
	def isoFormat(self, compact = True):
		# for compatibility
		return self.toiso(compact)

	def toNumeric(self):
		pass

	def toDict(self):
		result = {
			'year':   self.year,
			'month':  self.month,
			'day':    self.day,
			'hour':   self.hour,
			'minute': self.minute,
			'second': self.second,
			'microsecond': self.microsecond
		}
		return result

	def toTuple(self):
		result = (
			self.year, self.month, self.day,
			self.hour, self.minute, self.second, self.microsecond
		)
		return result

if __name__ == "__main__":
	string = '2008-04-18T15:52:09.000Z'

	result = Timestamp(string)

	print('Input: ', string)
	print("Output: ", result)