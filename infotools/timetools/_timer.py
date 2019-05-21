"""
	A simple timer for tracking how long snippets of code take to run.
"""
import time
from typing import Callable, Union, Dict, Tuple
import datetime
import numpy

from infotools.timetools import Duration
from infotools import numbertools

Number = Union[int, float]


class Timer:
	""" A class with convienient timing methods.
		.timeit -> Times a number of loops
		.timeFunction -> benchmarks a function
		.benchmark -> benchmarks an external process and returns
			both the average execution time and standard deviation.
	
	"""

	def __init__(self, func = None, *args, **kwargs):
		self.start_time = time.clock()
		self.end_time = 0.0
		if func is not None:
			self.timeFunction(func, *args, **kwargs)

	def __str__(self):
		return self.to_iso()

	def duration(self) -> float:
		return time.clock() - self.start_time

	def isOver(self, limit: Number = 10.0) -> bool:
		""" Checks if more time has elapsed than the supplied limit.
			Parameters
			----------
				limit: int, float; default 10.0
					The time limit, in seconds. 
					If more than <limit> seconds have passed, returns True
			Returns
			----------
				duration : bool
		"""
		result = self.duration() >= limit
		return result

	def togo(self, done: int, total: int, iso: bool = False) -> Duration:
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
			remaining = Duration(remaining).to_iso()
		return remaining

	def reset(self) -> None:
		self.start_time = time.clock()

	def split(self, label: str = 'the previous process'):
		""" Prints the elapsed time, then resets the timer.
			Parameters
			----------
				label: string; default "the previous process"
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
			string = "Finished {} in {}".format(label, self.to_iso())
		print(string, flush = True)
		self.reset()

	def benchmark(self, loops: int = 1) -> Dict[str, Number]:
		""" Returns a dictionary with information on the loop timing.
		
			Returns
			-------
				result: dict<>
					* 'duration': int
						The total time that has passed.
					* 'perLoop': float
						The average number of seconds passed for every loop.
					* 'loops': int
						Number of loops passed to the function.
		"""
		duration = self.duration()
		per_loop = duration / loops

		result = {
			'duration': Duration(duration),
			'perLoop':  per_loop,
			'loops':    loops
		}
		return result

	def timeFunction(self, func: Callable, *args, **kwargs) -> Tuple[str, str]:
		""" Benchmarks a function. args and kwargs are passed on to the function.
			Prints a message of the form 'a ± b per loop [c, d] where:
				* 'a': average time for each loop to execute. 
				* 'b': standard deviation for each loop. 
				* 'c': The fastest time any given loop completed. 
				* 'd': The slowest time any given loop took to complete.
			Parameters
			----------
			func: callable
				The function to benchmark.
			* 'loops': int; default 10
				The number of times to run the function during the benchmark.
			Returns
			-------
				result: tuple -> float, float
					The average and standard deviation of the loop execution times.
		"""
		if 'loops' in kwargs:
			loops = kwargs.pop('loops')
		else:
			loops = 100
		_results = list()

		for _ in range(loops):
			self.reset()
			func(*args, **kwargs)
			_results.append(self.duration())
		_results = numpy.array(_results)
		minimum = min(_results)
		maximum = max(_results)

		minimum = numbertools.human_readable(minimum)
		maximum = numbertools.human_readable(maximum)
		avg = numbertools.human_readable(_results.mean())
		std = numbertools.human_readable(_results.std())
		print("{}s ± {}s per loop [{} loops][{}s, {}s]".format(avg, std, loops, minimum, maximum))
		return avg, std

	def timeit(self, loops: int = 1, label: str = None):
		""" Calculates the time for a loop(s) to execute. Resets the timer.
			Parameters
			----------
				loops: int
					The total number of loops that were executed.
				label: string
					Added to the timeit message if provided.
			Return
			----------
				duration : string
					a string of the form 'a per loop (b for c loops)'
					* 'a': The average execution time for each loop 
					* 'b': The total execution time
					* 'c': The number of loops executed.
		"""
		benchmark = self.benchmark(loops)
		duration = benchmark['duration']
		per_loop = numbertools.human_readable(benchmark['perLoop'])

		if label is None:
			message = ""
		else:
			message = label + ': '

		message = message + "{0}s per loop ({1:.2f}s for {2:n} loop(s)) ".format(per_loop, duration, loops)

		self.reset()
		return message

	def to_iso(self) -> str:
		"""Returns an ISO duration representation of the elapsed time."""
		seconds = self.duration()

		return Duration(datetime.timedelta(seconds = seconds), unit = 'Seconds').toiso()

	def show(self, label: str = None) -> None:
		""" Prints the current time elapsed to stdout."""
		if label is not None:
			label += ': '
		else:
			label = ''
		print(label, "{0:.3f} seconds...".format(self.duration()), flush = True)


def benchmark(loops = 10, label = None):
	def my_decorator(func):
		_loops_to_excecute = loops

		def wrapped(*args, **kwargs):
			start = time.time()
			for index in range(loops):
				result = func(*args, **kwargs)
			end = time.time()
			duration = end - start

			per_loop = numbertools.human_readable(duration / _loops_to_excecute)
			message = f"{per_loop}s per loop ({duration:.2f}s for {_loops_to_excecute:n} loops) "
			if label:
				print(label)
			print(message)
			return result

		return wrapped

	return my_decorator


if __name__ == "__main__":
	@benchmark(loops = 100)
	def _function():
		100 ** 100


	_function()
