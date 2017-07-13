
from ._timestamp import Timestamp

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
	time_left = timer.togo(loop_number, total_loops, iso = True)
	if loop_number % loop_block < 1:
			print(
				"{loop:<6}{complete:>6.1%} {left}".format(
				loop = loop_number,
				complete = _percent_complete,
				left = time_left),
				flush = True
			)

def now():
	return Timestamp.now()