"""
	A simple timer for tracking how long snippets of code take to run.
"""
import statistics
import time
from typing import Callable, Dict, Tuple, Union

try:
	from infotools.timetools import Duration
	from infotools import numbertools
except ModuleNotFoundError:
	from .. import numbertools
	from ._duration import Duration

Number = Union[int, float]


class Timer:
	""" A class with convienient timing methods.
		.timeit -> Times a number of loops
		.timeFunction -> benchmarks a function
		.benchmark -> benchmarks an external process and returns
			both the average execution time and standard deviation.
	
	"""

	def __init__(self):
		self.start_time = time.clock()
		self.end_time = 0.0

	def __str__(self):
		return self.duration.to_iso()

	@property
	def duration(self) -> Duration:
		return Duration(time.clock() - self.start_time)

	def is_over(self, limit: Number = 10.0) -> bool:
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
		result = self.duration.total_seconds() >= limit
		return result

	def togo(self, done: int, total: int) -> Duration:
		""" Calculates the remaining time until a loop is finished
			executing
			Parameters
			----------
				done: int
					The number of loops that have already passed
				total: int
					The total number of loops expected
			Returns
			----------
				remaining : float, string
		"""
		if done == 0: done += 1
		perloop = self.duration / done
		remaining = (total - done) * perloop
		return Duration(remaining)

	def reset(self) -> None:
		self.__init__()

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
		duration = self.duration
		per_loop = duration / loops

		result = {
			'duration': Duration(seconds = duration),
			'perLoop':  per_loop,
			'loops':    loops
		}
		return result

	def time_function(self, func: Callable, *args, **kwargs) -> Tuple[str, str]:
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
		minimum = min(_results)
		maximum = max(_results)

		minimum = numbertools.human_readable(minimum)
		maximum = numbertools.human_readable(maximum)
		avg = numbertools.human_readable(statistics.mean(_results))
		std = numbertools.human_readable(statistics.stdev(_results))
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
