def memory_usage(show = True, units = 'MB'):
	""" Gets the current memory usage 
		Returns
		----------
			if show is False
			memory: int
				The total number of bytes being used by the current process
	"""
	import psutil
	process = psutil.Process(os.getpid())
	usage = process.memory_info().rss
	if show:
		if units == 'MB':
			value = usage / 1024**2
		print("Current memory usage: {0:.2f}{1}".format(value, units), flush = True)
	else:
		return usage