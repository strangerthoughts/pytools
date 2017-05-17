import pandas as pandas
import re
import datetime
import time
import math
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
    def __init__(self):
        self.start_time = time.clock()
        self.end_time = 0.0 
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
        self.__init__()
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
    def timeFunction(self, function, loops = 100, **kwargs):
        """ Benchmarks a function. Kwargs are passed on to the function.
        """
        self.reset()
        for i in range(loops):
            function(**kwargs)
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

class DurationOBS:
    def __init__(self, value = None, units = None):
        """ Stores Time Differentials.
            Internally operates on a datetime.timedelta object
        """
        self.version = 'V2.0.0'
        self._define_conversions()
        self._define_regexes()
        if value is None:
            _duration = datetime.datetime.now() - datetime.datetime.today()
            #raise ValueError("Duration(value = {0}, units = {1})".format(value, units))
        elif isinstance(value, pandas.Timedelta):
            days = value.days
            seconds = value.seconds
            microseconds = value.microseconds
            _duration = datetime.timedelta(days = days, 
                                           seconds = seconds, 
                                           microseconds = microseconds)
        elif isinstance(value, datetime.timedelta):
            _duration = value
        elif isinstance(value, Duration):
            _duration = value.duration
        elif isinstance(value, str):
            _duration = self._from_str(value)
        elif isinstance(value, (int, float)) and units is not None:
            _duration = self._from_numeric(value, units)
        else:
            #raise ValueError("Duration(value = {0}, units = {1}".format(value, units))
            _duration = datetime.timedelta(seconds = 0)
        self.duration = _duration
    def __abs__(self):
        return Duration(abs(self.duration))
    def __repr__(self):
        return "Duration({0})".format(self.to_iso())
    def __str__(self):
        return self.to_iso()
    def __add__(self, other):
        if isinstance(other, Duration):
            return self.duration + other.duration
        elif isinstance(other, pandas.Timedelta):
            return self.duration + other
        elif isinstance(other, datetime.timedelta):
            return self.duration + other
    def __sub__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration - other
        elif isinstance(other, Duration):
            return Duration(self.duration - other.duration)
    def __div__(self, other):
        if isinstance(other, int):
            return Duration(self.duration / other)
    def __rsub__(self, other):
        if isinstance(other, pandas.Timedelta):
            return other - self.duration
        elif isinstance(other, Duration):
            return Duration(other.duration - self.duration)
        else:
            return self.__sub__(-other)
    def __rdiv__(self, other):
        if isinstance(other, int):
            return Duration(other / self.duration)
    def __eq__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration == other
        if isinstance(other, datetime.timedelta):
            return self.duration == other
        if isinstance(other, Duration):
            return self.duration == other.duration
    def __ne__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration != other
        if isinstance(other, datetime.timedelta):
            return self.duration != other
        if isinstance(other, Duration):
            return self.duration != other.duration
    def __lt__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration < other
        if isinstance(other, datetime.timedelta):
            return self.duration < other
    def __le__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration <= other
        if isinstance(other, datetime.timedelta):
            return self.duration <= other
        if isinstance(self.duration, Duration):
            return self.duration <= other.duration
    def __gt__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration > other
        if isinstance(other, datetime.timedelta):
            return self.duration > other
        if isinstance(other, Duration):
            return self.duration > other.duration
    def __ge__(self, other):
        if isinstance(other, pandas.Timedelta):
            return self.duration >= other
        if isinstance(other, datetime.timedelta):
            return self.duration >= other  
        if isinstance(other, Duration):
            return self.duration >= other.duration
    
    def _define_conversions(self):
        #number of days in the selected unit
        days = {
            'Years': 365,
            'Months': 30.42,
            'Weeks': 7,
            'Days': 1,
            'Seconds': 1 / 86400 
        }
        #number of seconds in the selected unit
        seconds = {
            'Days': 86400,
            'Hours': 3600,
            'Minutes':60,
            'Seconds': 1,
            'Microseconds': 1 / 1000000
        }
        
        weeks =   {k: (v / days['Weeks'])     for k, v in days.items()}
        months =  {k: (v / days['Months'])    for k, v in days.items()}
        years =   {k: (v / months['Years'])   for k, v in months.items()}
        minutes = {k:(v / seconds['Minutes']) for k, v in seconds.items()}
        hours =   {k: (v / minutes['Hours'])  for k, v in minutes.items()}
        
        self.convert = {
            'Years': years,
            'Months': months,
            'Weeks': weeks,
            'Days': days,
            'Hours': hours,
            'Minutes': minutes,
            'Seconds': seconds
        }
    
    def _define_regexes(self):
        self.iso_regex = re.compile(r"(\d+(?:\.\d+)?[A-Z])")
        self.iso_duration = re.compile(r"P(?:\d+(?:\.\d+)?[YMWDHMST]{1,2})+")
        self.iso_timestamp = re.compile(r"\d{4}[-]\d{2}[-]\d{2}[\sT]\d{2}[:]\d{2}[:]\d{2}")
        
    def divide(self, other):
        return Duration(self.duration / other)
    def _from_interval(self, value):
        #<start>/<end>      "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"
        #<start>/<duration> "2007-03-01T13:00:00Z/P1Y2M10DT2H30M"
        #<duration>/<end>   "P1Y2M10DT2H30M/2008-05-11T15:30:00Z"
        left, right = value.split('/')
    def _from_iso(self, value, from_weeks = False):
        value = value.split('T')
        dates = self.iso_regex.findall(value[0])
        times = self.iso_regex.findall(value[1])
        
        dates = {m[-1]:int(m[:-1]) for m in dates}
        times = {m[-1]:(float(m[:-1]) if m[-1] == 'S' else int(m[:-1])) for m in times}
        
        days = (dates.get('Y', 0) * 365) + (dates.get('M', 0) * 30) + dates.get('D', 0)
        minutes = (times.get('H', 0) * 60) + times.get('M', 0)
        seconds = times.get('S', 0)
        milliseconds = (seconds - int(seconds)) * 1000
        microseconds = (milliseconds - int(milliseconds)) * 1000
        
        duration = datetime.timedelta(days = days, 
                                           minutes = minutes, 
                                           seconds = int(seconds),
                                           milliseconds = int(milliseconds),
                                           microseconds = int(microseconds))
        return duration
            
    def _from_numeric(self, value, units):
        
        if units in ['Years', 'Months', 'Days']:
            days = value / self.convert[units]['Days']
            _duration = datetime.timedelta(days = days)
        
        elif units in ['Hours', 'Minutes', 'Seconds']:
            seconds = value * self.convert[units]['Seconds']
            _duration = datetime.timedelta(seconds = seconds)
        return _duration
        
    def _from_str(self, value):
        if '-' in value or ':' in value:
            _duration = self._from_timestamp(value)
        else:
            _duration = self._from_iso(value)
        return _duration
    def _from_timestamp(self, value):
        #P3Y6M4DT12H30M5S
        #P0003-06-04T12:30:05
        if 'T' in value:
            dates, times = value.split('T')
        else:
            dates, times = value.split(' ')
        #----------------------------FORMAT DATES---------------------------
        dates = dates[1:].split('-')
        dates = list(map(int, dates))
        #----------------------------FORMAT TIMES---------------------------
        times = times.split(':')
        times = list(map(int, times))
        
        _duration = self._from_tuple(dates + times)
        print(_duration)
        return _duration
    def _from_tuple(self, value):
        years, months, days, hours, minutes, seconds, *microseconds = value
        if len(microseconds) == 0: microseconds = 0
        weeks = years * self.convert['Weeks']['Years']

        days += months * self.convert['Days']['Months']
        
        for i in (years, weeks, days, hours, minutes, seconds):
            print(type(i), i)
        
        _duration = datetime.timedelta(weeks = weeks, days = days, 
                                 hours = hours, minutes = minutes, seconds = seconds,
                                 microseconds = microseconds)
        return _duration
    def to_common(self):
        years, months, days, hours, minutes, seconds, microseconds = self.to_tuple()
        common_string = ''
        for value, suffix in zip([years, months, days, hours, minutes, seconds],
                                 [' Years, ', ' Months, ', ' Days, ', ' Hours, ', ' Minutes, ', ' Seconds']):
            if not math.isclose(value, 0.0, abs_tol = 0.04):
                common_string += '{0}{1}'.format(value, suffix)
        return common_string
    def to_iso(self, flag = 'short', precision = 2):
        """
            flags:
                short: drops 00 portions of th duration
                long:  keeps nonzero values
                time: shows the time portion of the duration
                date: shows the date portion of the duration
        """
        years, months, days, hours, minutes, seconds, microseconds = self.to_tuple()
        seconds += microseconds / 1000000
        
        iso_string = 'P'
        for value, suffix in zip([years, months, days, hours, minutes, seconds],
                                 ['Y', 'M', 'D', 'H', 'M', 'S']):
            if not math.isclose(value, 0.0, abs_tol = .000001):
                _substring = '{0:>02g}{1}'
                iso_string += _substring.format(value, suffix)
            if suffix == 'D':
                iso_string += 'T'
        return iso_string
    def to_numeric(self, units):
        #years, months, days, hours, minutes, seconds, microseconds = self.to_tuple()
        #dates = (years * 365) + (months * 30) + days
        #times = (hours * 3600)+ (minutes * 60) + seconds
        days =         self.duration.days
        seconds =      self.duration.seconds
        microseconds = self.duration.microseconds
        
        if units in ['Years', 'Months', 'Days']:
            days +=  seconds * self.convert['Days']['Seconds']
            _duration = days / self.convert['Days'][units]
            
        elif units in ['Hours', 'Minutes', 'Seconds']:
            seconds += days * self.convert['Seconds']['Days']
            _duration = seconds / self.convert['Seconds'][units]
        
        return _duration    
    def to_timedelta(self):
        return self.duration
    def to_Timedelta(self):
        return pandas.Timedelta(self.duration)
    def to_tuple(self):
        days = self.duration.days
        seconds = self.duration.seconds
        microseconds = self.duration.microseconds
        
        #----------------Format the date portion------------------
        date = dict()
        years, days = divmod(days, 365)
        months,days = divmod(days, 30)
               
        
        #----------------Format the time portion------------------
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds=divmod(seconds, 60)
        
        return (years, months, days, hours, minutes, seconds, microseconds)

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
        ((?P<years>[\d]+)[yY])?
        ((?P<months>[\d]+)[mM])?
        ((?P<weeks>[\d]+)[wW])?
        ((?P<days>[\d]+)[dD])?
        [tT]?
        ((?P<hours>[\d]+)[hH])?
        ((?P<minutes>[\d]+)[mM])?
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
    def _parseGenericObject(cls, generic, force = True):
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
            message = "Unsupported generic type: {}".format(generic)
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
        elif isinstance(element, (int, float)):
            result = cls._parseNumber(element, **kwargs)
        else: result = cls._parseGenericObject(element, **kwargs)
        return result
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
            elif key == 'days': days += item()
            elif key == 'weeks': days == 7 * weeks
            elif key == 'months': days == 30*item
            elif key == 'years': days = 365*years
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

        return isostring


class Timestamp:
    def __init__(self, value):
        self._define_regexes()
        if isinstance(value, (tuple, list)):
            _timestamp = self._from_tuple(value)
        elif isinstance(value, str):
            if ':' in value:
                _timestamp = self._from_iso(value)
            else:
                _timestamp = self._from_long(value)
        elif isinstance(value, (int, float)):
            _timestamp = self._from_numeric(value)
        self.timestamp = _timestamp
    def __str__(self):
        return str(self.timestamp)
    def __repr__(self):
        return "Timestamp({0})".format(self.timestamp)
    def _define_regexes(self):
        date_regex = r"""(\d{1,4})
                         [-/]
                         (\d{1,2})
                         [-/]
                         (\d{2})"""
        self.date_regex = re.compile(date_regex, re.VERBOSE)
        self.timestamp_regex = re.compile(r"(\d{4})-(\d{2})-(\d{2}).(\d{2}):(\d{2}):(\d{2}(\.\d+)?)")
        
        self.time_regex = re.compile(r"(\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d+)?)")
        self.long_regex = re.compile(r"(\w+)\s(\d+)[A-Za-z,]*\s(\d{4})")
    
    def _from_iso(self, value):
        date = self.date_regex.findall(value)
        time = self.time_regex.findall(value)
        print(date)
        print(time)
        if len(date) == 0: date = [0, 0, 0]
        else: date = [int(i) for i in date[0]]
            
        if len(time) == 0: time = [0, 0, 0]
        else: time = [(int(i) if '.' not in i else float(i)) 
                        for i in time[0] if i != '']
        _timestamp = self._from_tuple(date + time)       
        
        return _timestamp
    def _from_numeric(self, value, flag = 'excel'):
        if flag is None:
            pass
        elif flag == 'excel':
            _timestamp = self._from_excel(value)
            
        return _timestamp
    def _from_excel(self, value):
        value += datetime.date(year = 1899, month = 12, day = 30).toordinal()
            
        xldate, xltime = divmod(value, 1)
        date = datetime.date.fromordinal(int(xldate))
        #------------------Convert Time------------------       
        second = xltime * (3600 * 24)
        microsecond = 0
        second = int(second)
        hour, second = divmod(second, 3600)
        minute, second = divmod(second, 60)
        microsecond = 0
        
        time = datetime.time(hour = hour, minute = minute, 
                             second = int(second))
        
        _timestamp = datetime.datetime.combine(date, time)
        return _timestamp
    def _from_timestamp(self, value):
        pass
    @staticmethod
    def _from_tuple(value, flag = None):
        if len(value) >= 6:
            year, month, day, hour, minute, second, *microsecond = value
        elif flag in 'Datedate':
            year, month, day = value
            hour, minute, second, microsecond = 0,0,0,0
        elif flag in 'Timetime':
            year, month, day = 0, 0, 0
            hour, minute, second, *microsecond = value
        if isinstance(second, float):
            second, microsecond = divmod(second, 1)
            second = int(second)
            microsecond = int(microsecond * 1000000)
        
        if isinstance(microsecond, list):
            if len(microsecond) == 0:
                microsecond = 0
            else:
                microsecond = microsecond.pop()
        
        _timestamp = datetime.datetime(year = year, month = month, day = day,
                                       hour = hour, minute = minute, second = second,
                                       microsecond = microsecond)
        return _timestamp
    def _from_long(self, value):
        matches = self.long_regex.findall(value)
        print(matches)
    def _from_datetime(value, flag):
        if flag in 'Datedate':
            pass
        elif flag in 'Timetime':
            pass
    def to_datetime(self):
        return self.timestamp
    def to_excel(self):
        pass
    def to_iso(self, sep = ' ', iso_week = False):
        year, month, day, hour, minute, second, microsecond = self.to_tuple()
        date = (year, month, day)
        time = (hour, minute, second + (microsecond / 1000000))
        
        _timestamp = "{0}-{1}-{2}{3}{4}:{5}:{6}".format(*date, sep, *time)
        return _timestamp
    def to_long(self):
        pass
    def to_numeric(self, flag = 'excel'):
        pass
    def to_utctimestamp(self):
        pass
    def to_tuple(self):
        return (self.timestamp.year,
                self.timestamp.month,
                self.timestamp.day,
                self.timestamp.hour,
                self.timestamp.minute,
                self.timestamp.second,
                self.timestamp.microsecond)

if __name__ == "__main__":
    duration = "P1Y2M10DT2H30M"
    duration = Duration(3, 'seconds')
    print(duration)