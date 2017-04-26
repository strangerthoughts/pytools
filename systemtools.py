import os
import shlex

def memoryUsage(show = True, units = 'MB'):
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

def Terminal(command, label = "", filename = None):
	""" Calls the system shell.
		Parameters
		----------
			command: string
				The command to run.
			label: string
				Used to mark output in the console.
			filename: string
				If not None, will output to console as a file.
	"""
	#print("Terminal(label = {0})".format(label))
	terminal_log = os.path.join(PIPELINE_DIRECTORY, "0_config_files", "terminal_log.log")
	terminal_label = "{0} {1}".format(label, generateTimestamp())
	terminal_label  = '--'*15 + terminal_label + '--'*15 + '\n'
	terminal_label += '..'*40 + '\n'
	terminal_label += " ".join(shlex.split(command)) + '\n'
	terminal_label += '..'*40 + '\n'
	terminal_label += '--'*40 + '\n'

	#Try using exceptions to catch timeout errors
	#logging.info("System Command: " + str(command))
	#if filename is None:
	if filename is None:
		#print(terminal_label)
		process = os.system(command)
		output = ""
	else:
		command = shlex.split(command)
		process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		output = str(process.stdout.read(),'utf-8')
		updateConsoleLog(filename, command, output, label)


	return output

def updateConsoleLog(filename, command, output, label = ""):
	if os.path.exists(filename): opentype = 'a'
	else: opentype = 'w'
	with open(filename, opentype) as console_file:
		console_file.write(now().isoformat() + ': ' + label + '\n')
		console_file.write(' '.join(command) + '\n')
		console_file.write(output + '\n\n')