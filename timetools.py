import pandas as pandas
import re
import datetime
import time
import math
"""
        if index % 5000 < 1:
            print("{0:<6}{1:>6.1%} {2}".format(index, index / len(patients), 
                timer.togo(index, len(patients), iso = True)), flush = True)
"""

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
    def __init__(self, clock = True):
        self.clock = clock
        if self.clock:
            self.start_time = time.clock()
        else:
            self.start_time = time.time()
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
    def timeit(self, value):
        """ Calculates the time for a loop to execute
            Parameters
            ----------
                value: int
                    The number of loops executed
            Return
            ----------
                duration : string
        """
        duration = self.duration()
        string = "{0:.2f} us per loop, ".format(duration * 1000000 / value)
        string += "total of {0:.2f} seconds ".format(duration) 
        string +="and {0:n} loops.".format(value)
        return string
    def to_iso(self):
        """Returns an ISO duration of the elapsed time"""
        seconds = time.clock() - self.start_time
        return Duration(seconds, 'Seconds').to_iso()
    def show(self, label = None):
        if label is not None:   label += ': '
        else:                   label = ''
        print(label, "{0:.3f} seconds...".format(self.duration()), flush = True)

class Duration:
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
    #@staticmethod
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
