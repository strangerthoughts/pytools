import time
import datetime
import re

from numbers import Number

from ._duration import Duration 
from .. import numbertools

class Timer:
	def __init__(self, func = None, *args):
		self.start_time = time.clock()
		self.end_time = 0.0 
		if func is not None:
			self.timeFunction(func, 100, *args,)

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
		result = self.duration() > limit
		return result

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

	def timeFunction(self, func, loops = 10, *args, **kwargs):
		""" Benchmarks a function. Kwargs are passed on to the function.
		"""
		_results = list()
		
		for i in range(loops):
			self.reset()
			func(*args, **kwargs)
			_results.append(self.duration())

		minimum = min(_results)
		maximum = max(_results)
		avg = sum(_results) / len(_results)
		std = numbertools.standardDeviation(_results)

		minimum = numbertools.humanReadable(minimum)
		maximum = numbertools.humanReadable(maximum)
		avg = numbertools.humanReadable(avg)
		std = numbertools.humanReadable(std)
		print("{}s ± {}s per loop [{} loops][{}s, {}s]".format(avg, std, loops, minimum, maximum))
		return avg, std

	def timeit(self, loops = 1, label = None):
		""" Calculates the time for a loop to execute
			Parameters
			----------
				loops: int
					The total number of loops that were executed.
				label: string
					Added to the timeit message if provided.
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
		seconds = self.duration()
		return Duration(seconds, unit = 'Seconds').toiso()

	def show(self, label = None):
		if label is not None:   label += ': '
		else:                   label = ''
		print(label, "{0:.3f} seconds...".format(self.duration()), flush = True)