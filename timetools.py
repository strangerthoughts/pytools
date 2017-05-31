import datetime
import math
import pandas
import re
import time

from pprint import pprint
from numbers import Number

#Import local files.
try:
    import pytools.numbertools as numbertools
except:
    import numbertools

def elapsed(loop_number, loop_block, total_loops, timer):
    """ Prints a line indicating the elapsed progress of the loop described
        Parameters
        ----------
            loop_number: int
                The number of loops passed
            loop_block: int
                The number of loops to wait before updating the console
            total_loops: int
                The number of loops expected
            timer: timetools.Timer
                The timetools.Timer object used to track the current loop
        Returns
        ----------
            function : None
        """
    _percent_complete = loop_number / total_loops
    if loop_number % loop_block < 1:
            print("{loop:<6}{complete:>6.1%} {left}".format(
                        loop = loop_number, 
                        complete = _percent_complete, 
                        left = timer.togo(_percent_complete, iso = True)), 
                flush = True)

class Timer:
    def __init__(self, function = None, *args):
        self.start_time = time.clock()
        self.end_time = 0.0 
        if function is not None:
            self.timeFunction(function, 100, *args,)
    def __str__(self):
        return self.to_iso()
    def __repr__(self):
        return "Timer({0})".format(self.to_iso())
    def duration(self):
        self.end_time = time.clock()
        return self.end_time - self.start_time
    def isover(self, limit = 10.0):
        """ Checks if more time has elapsed than the supplied limit
            Parameters
            ----------
                limit: int, float; default 10.0
                    The time limit, in seconds. 
                    If more than <limil> seconds have passed, returns True
            Returns
            ----------
                duration : bool
        """
        return self.duration() > value
    def togo(self, done, total, iso = False):
        """ Calculates the remaining time until a loop is finished
            executing
            Parameters
            ----------
                done: int
                    The number of loops that have already passed
                total: int
                    The total number of loops expected
                iso: bool; default False
                    Whether to format the result as an ISO duration
            Returns
            ----------
                remaining : float, string
        """
        if done == 0: done += 1
        perloop = self.duration() / done
        remaining = (total - done) * perloop
        if iso:
            remaining = Duration(remaining, 'Seconds').to_iso()
        return remaining
    def reset(self):
        #self.__init__() Would mess up the input if used as a decorator
        self.start_time = time.clock()
    def split(self, label = 'the previous process'):
        """ Prints the elapsed time, then resets the timer
            Parameters
            ----------
                label: string, int; default "the previous process"
                    Used to indicate which process was timed. If int, will
                    print the number of milliseconds required to run the 
                    previous loop instead
            Returns
            ----------
                function : None
        """
        _duration = self.duration()
        if isinstance(label, int):
            string = self.timeit(label)
        else:
            string = "Finished {0} in {1}".format(label, self.to_iso())
        print(string, flush = True)
        self.reset()
    def benchmark(self, loops = 1):
        """ Returns a dictionary with information on the loop timing"""
        duration = self.duration()
        per_loop = duration / loops

        result = {
            'duration': duration,
            'perLoop': per_loop,
            'loops': loops
        }
        return result
    def timeFunction(self, function, loops = 100, *args):
        """ Benchmarks a function. Kwargs are passed on to the function.
        """
        self.reset()
        for i in range(loops):
            function(*args)
        self.timeit(loops)
    def timeit(self, loops = 1, label = None):
        """ Calculates the time for a loop to execute
            Parameters
            ----------
                value: int
                    The number of loops executed
            Return
            ----------
                duration : string
        """
        benchmark = self.benchmark(loops)
        duration = benchmark['duration']
        per_loop = numbertools.humanReadable(benchmark['perLoop'])
        
        if label is None: message = ""
        else: message = label + ': '
        
        message = message + "{0}s per loop ({1:.2f}s for {2:n} loop(s)) ".format(per_loop, duration, loops)
        
        print(message)
        self.reset()
        return message
    def to_iso(self):
        """Returns an ISO duration of the elapsed time"""
        seconds = time.clock() - self.start_time
        return Duration(seconds, unit = 'Seconds').toiso()
    def show(self, label = None):
        if label is not None:   label += ': '
        else:                   label = ''
        print(label, "{0:.3f} seconds...".format(self.duration()), flush = True)

class Duration(datetime.timedelta):
    """ Inherits from datetime.timedelta. Designed to interprete
        many forms of timedelta representations.
        Notes
        -----
            Each 1 month duration is converted to a 30 day duration,
            and each 1 year duration is converted to a 365 day duration.
        Supported Formats
        -----------------
            ISO Duration: string
                Format: P[nnY][nnM][nnW][nnD]T[nnH][nnM][nn.nnnS] (may be lowercase)
            ISO Interval: string
                Format: [Timestamp]/[Timestamp], [ISO Duration]/[Timestamp], [Timestamp]/[ISO Duration]
                Notes: if a combined timestamp/ duration is given, only the duration part is used.
            Datetime Tuple: Tuple<number x {6,7}>
                A tuple containing the number values for each datetime field.
                Format: (years, months, days, hours, minutes, seconds)
            Number: Called with Duration([number], [unit]), where 'unit' is any of the datetime.timedelta supported types.
            Generic Objects: Any object with days/seconds/microseconds attributes, 
                a .total_seconds() method, or a .to_timedelta() method.
    """
    duration_regex = re.compile(r"""
        [pP]?
        ((?P<years>[\d]+)[yY])?[-]?
        ((?P<months>[\d]+)[mM])?[-]?
        ((?P<weeks>[\d]+)[wW])?[-]?
        ((?P<days>[\d]+)[dD])?
        [tT]?
        ((?P<hours>[\d]+)[hH])?[-]?
        ((?P<minutes>[\d]+)[mM])?[-]?
        ((?P<seconds>[\d]+(.[\d]+)?)[sS])?""", re.VERBOSE)
    timestamp_regex = re.compile(r"""
        (?P<date>[\d]{4}-[\d]{2}-[\d]{2})?[\sT]?
        (?P<time>[\d]{2}:[\d]{2}:[\d]{2}(\.[\d]+)?)?""", re.VERBOSE)

    readable_regex = ""
    def __new__(cls, value = None, unit = None, **kwargs):
        """
            Keyword Arguments
            -----------------
            All arguments are optional and default to 0. 
            Arguments may be integers or floats, and may be positive or negative.
                days:         number; defualt 0
                seconds:      number; default 0
                microseconds: number; default 0
                milliseconds: number; default 0
                minutes:      number; default 0
                hours:        number; default 0
                weeks:        number; default 0
        """
        if value is None: datetime_keys = kwargs
        else: 
            if unit is not None: kwargs['unit'] = unit
            datetime_keys = cls._parseInput(value, **kwargs)
        return super().__new__(cls, **datetime_keys)
    def __str__(self):
        return self.toiso()
    @classmethod
    def _parseGenericObject(cls, generic, force = False, **kwargs):
        """ Attempts to parse a generic timedelta object. If all attempts
            to extract information from the object fail and 'force' = True (default),
            then a 0-length Duration object is created instead.
        """
        generic_values = dict()
        #Try extracting the day, seconds, and microseconds from the object.
        try:
            generic_values['days'] = generic.days
            generic_values['seconds'] = generic.seconds
            generic_values['microseconds'] = generic.microseconds
            return generic_values
        except: pass
        #Try extracting the total number of seconds contained in the object
        try:
            generic_values['seconds'] = generic.total_seconds()
            return generic_values
        except: pass

        #Try to extract a more usable object type
        try:
            generic_values = generic.to_timedelta()
            return cls._parseGenericObject(generic_values)
        except: pass
        if force:
            return {'seconds': 0}
        else:
            message = "Unsupported generic type: {} ({})".format(generic, type(generic))
            raise ValueError(message)
    @classmethod
    def _parseHumanReadable(cls, string):
        """ Parses durations written in common non-numerical formats."""
        print("._parseHumanReadable() is Currently not Implemented!")
    @classmethod
    def _parseInterval(cls, value):
        """ Parses an ISO interval.
            Supported Formats:
                <start>/<end>      Ex. "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"
                <start>/<duration> Ex. "2007-03-01T13:00:00Z/P1Y2M10DT2H30M"
                <duration>/<end>   Ex. "P1Y2M10DT2H30M/2008-05-11T15:30:00Z"
            Returns
            -------
                Duration
        """
        leftright = value.split('/')
        left = leftright[0]
        right = leftright[1] if len(leftright) != 1 else ""
        if '-' in left and '-' in right: result = cls(Timestamp(right) - Timestamp(left))
        elif '-' not in left:  result = cls._parseiso(left)
        elif '-' not in right: result = cls._parseiso(right)
        else:
            message = "Invalid format passed to timetools.{}: {}".format(str(cls), value)
            raise TypeError(message)

        return result

    @classmethod
    def _parseiso(cls, string):
        """ Parses a string with formatted as an ISO duration: PnnYnnMnnWnnDTnnHnnMnnST """
        matches = cls.duration_regex.search(string).groupdict()
        for k, v in matches.items():
            if v is None: v = 0
            else: v = float(v)
            matches[k] = v
        if 'years' in matches:  matches['days'] += 365 * matches.pop('years')
        if 'months' in matches: matches['days'] += 30  * matches.pop('months')

        #return cls(**matches)
        return matches
    @classmethod
    def _parseInput(cls, element, **kwargs):
        """ Chooses which parse to apply to the input, if supported."""
        if isinstance(element, str):
            result = cls._parseString(element)
        elif isinstance(element, tuple):
            result = cls._parseTuple(element)
        elif isinstance(element, (int, float, Number)):
            result = cls._parseNumber(element, **kwargs)
        else: result = cls._parseGenericObject(element, **kwargs)
        return result
    @classmethod
    def _parseNumericString(cls, string):
        pass
    @classmethod
    def _parseNumber(cls, number, **kwargs):
        """ parses a (number, unit) tuple. """
        days = 0
        seconds = 0
        microseconds = 0
        if 'unit' in kwargs: 
            kwargs = {kwargs['unit'].lower(): number} #Remove any other time values (seconds/days/etc.)

        for key, item in kwargs.items():
            key = key.lower()
            if key == 'seconds':seconds += item
            elif key == 'minutes':seconds += 60*item
            elif key == 'hours':seconds += 3600*item
            elif key == 'days': days += item
            elif key == 'weeks': days == 7 * weeks
            elif key == 'months': days == 30*item
            elif key == 'years': days = 365*item
            elif key == 'microseconds': microseconds += item
            elif key == 'milliseconds': microseconds += item / 1000
        result = {
            'microseconds': microseconds,
            'seconds': seconds,
            'days': days
        }
        return result
    @classmethod
    def _parseString(cls, string):
        if '/' not in string: result = cls._parseiso(string)
        elif len([i for i in string if not i.isdigit()]) < 3:
            result = self._parseNumericString(string)
        else: result = cls._parseInterval(string)
        return result
    @classmethod
    def _parseTimestamp(self, string):
        """ Parses durations formatted as Y:M:D:H:M:S. """
        pass
    @classmethod
    def _parseTuple(self, value):
        """ Returns a Duration object generated from a tuple of time values.
            Format: (years, months, days, hours, minutes, seconds[,microseconds])
        """
        years, months, days, hours, minutes, seconds, *microseconds = value

        if len(microseconds) == 1: microseconds = microseconds[0]
        if microseconds < 1: microseconds *= 1000000
        days += 365 * years + 30 * seconds

        result = {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'microseconds': microseconds
        }

        return result
    ######################### Public methods that return a Duration object #########################
    @classmethod
    def fromDict(self, keys):
        """ Parses a dict of time values. """
        return cls(**keys)
    @classmethod
    def fromString(cls, string):
        result = cls._parseString(result)
        return cls.fromDict(result)
    @classmethod
    def fromTuple(cls, value):
        result = cls._parseTuple(value)
        return cls.fromDict(result)
    ##################### Public Methods to convert the timedelta to another format ################
    def todict(self):
        """ Returns a dictionary that can be used to instantiate another timedelta or Duration object. """
        result = {
            'days': self.days,
            'seconds': self.seconds,
            'microseconds': self.microseconds
        }
        return result
    def tolongdict(self):
        """ Returns a dictionary with more human readable date and time keys. """
        original = self.todict()
        longdict = dict()
        #Get date values
        days = original['days']
        longdict['years'], days = divmod(days, 365)
        longdict['weeks'], longdict['days'] = divmod(days, 7)

        #Get time values
        seconds = original['seconds']
        longdict['hours'], seconds = divmod(seconds, 3600)
        longdict['minutes'], longdict['seconds'] = divmod(seconds, 60)
        longdict['seconds'] += original['microseconds'] / 1000000

        return longdict
    def isoformat(self):
        """ To make calls compatible with Timestamp.isoformat() """
        return self.toiso()
    def toiso(self, compact = True):
        """ Converts the timedelta to an ISO Duration string. By default, 
            weeks are used instead of months, so the original duration string
            used to create to Duration object may differ (but will be equivilant to)
            the output of this method.
            Parameters
            ----------
                compact: bool; default False
                    Whether to omit emty fields.
        """

        values = self.tolongdict()
        datetime_map = [
            'P', ('years', 'Y'), ('months', 'M'), ('weeks', 'W'), ('days', 'D'), 
            'T', ('hours', 'H'), ('minutes', 'M'), ('seconds', 'S')]
        isostring = ""
        for key in datetime_map:
            if isinstance(key, tuple):
                value = values.get(key[0], 0)
                if value == 0 and compact: continue
                else: isostring += str(value) + key[1]
            else:
                isostring += key
        isostring = ''.join(isostring)

        if isostring == 'PT' and not compact: #Duration of 0 seconds
            isostring = 'PT0S'
        if isostring[1] == 'P': isostring = isostring[1:]
        if isostring[-1] == 'T': isostring = isostring[:1]

        return isostring
    def totalSeconds(self):
        return self.total_seconds()
    def totalDays(self):
        values = self.todict()
        days = values['days'] + (24*3600*values['seconds'])
        return days
    def totalYears(self):
        return self.totalDays() / 365
    def to_numeric(self, units):
        """Backwords-compatible method"""
        units = units.lower()
        if units == 'days':
            value = self.totalDays()
        elif units == 'years':
            value = self.totalYears()
        elif units == 'months':
            value = self.totalYears()*12

        return value



class Timestamp(datetime.datetime):
    timestamp_regex = re.compile(
        r"""(?:(?P<year>[\d]{4})-(?P<month>[\d]{2})-(?P<day>[\d]{2}))?
            [\sA-Za-z]?
            (?:(?P<hour>[\d]+)[:](?P<minute>[\d]+)[:](?P<second>[\d]+))?""",
            re.VERBOSE)
    def __new__(cls, *args, **kwargs):

        #class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
        if len(args) == 1:
            result = cls._parseInput(args[0])
        elif len(args) == 3:
            result = {'year':args[0], 'month': args[1], 'day': arg[2]}
            result.update(kwargs)
        else:
            result = kwargs

        return super().__new__(cls,            
            result['year'], result['month'], result['day'],
            result.get('hour', 0), result.get('minute', 0), result.get('second', 0))

    @staticmethod
    def _cleandict(item):
        item = {k:(int(v) if v else 0) for k, v in item.items()}
        return item
    
    @classmethod
    def _parseExcel(cls, value):
        value += datetime.date(year = 1899, month = 12, day = 30).toordinal()
            
        xldate, xltime = divmod(value, 1)
        date = datetime.date.fromordinal(int(xldate))
        #------------------Convert Time------------------       
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
        date = cls._parseGenericDateObject(value)
        time = cls._parseGenericTimeObject(value)
        if date is None:
            message = "Invalid Date: {}".format(value)
            raise ValueError(message)
        date.update(time)
        return date
    @classmethod
    def _parseGenericDateObject(cls, element):
        try:
            date_values = {
                'year': element.year,
                'month': element.month,
                'day': element.day
            }
        except:
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
        except:
            time_values = dict()
        return time_values
    @classmethod
    def _parseInput(cls, value):
        if isinstance(value, str):
            if any(not c.isdigit() for c in value):
                result = cls._parseTimestamp(value)
            else:
                result = cls._parseNumericString(value)
        elif isinstance(value, (int, float)):
            result = cls._parseNumeric(value)
        else:
            result = cls._parseGenericObject(value)

        return result
    @classmethod
    def _parseDateTimeString(cls, string):
        """ parses a string formatted as a generic YY/MM/DD string. """
        if '-' in string and ':' in string:
            result = self._parseTimestamp(string)
        else:
            result = self._parseNumericInput(string)
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
    def getTime(self):
        return (self.hour, self.minute, self.second, self.microsecond)
    def toiso(self, compact = True):
        result = self.isoformat()
        if compact and not any(i!=0 for i in self.getTime()):
            result = result.split('T')[0]
        return result
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
        result = (self.year, self.month, self.day, 
            self.hour, self.minute, self.second, self.microsecond)
        return result

if __name__ == "__main__":
    d = "20160519"
    d= Timestamp(d)
    print(d)
    print(d.isoformat())
    print(d.toiso())