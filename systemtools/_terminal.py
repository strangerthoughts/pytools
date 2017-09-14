import os
import shlex
import subprocess
from pytools import timetools



class Terminal:
	def __init__(self, command, label = "", expected_output = None, command_filename = None, output_filename = None, verbose = 0, show_output = False):
		"""
			Parameters
			----------
				command: string
					The command to excecute.
				label: string
					A label to identify the process as it runs. Used mainly for debugging or to show 
					theprogress of multiple commands excecuted after each other.
				expected_output = string, list<string> [PATH]
					Files created by the command, if applicable. If the output files are not created,
					will raise an error.
				command_filename: string [PATH]; default None
					The command and arguments will be saved to this file.
				output_filename: string [PATH]; default None
					Any text printed to the console will be saved to the file located at the path provided.
				verbose: {0, 1, 2, 'label', 'command', 'full'}; default 0
					Determines how much text to print while the command runs.
						0: None
						1: Command Label
						2: Full output
		"""
		self.start_time = timetools.now()
		self.command = command
		self.label = label
		self.command_filename = command_filename
		self.output_filename = output_filename
		self.show_output = show_output
		self.output = ""
		self.verbose = verbose
		if isinstance(self.verbose, int): self.verbose = []

		if expected_output is None:
			self.expected_output = []
		elif isinstance(expected_output, str):
			self.expected_output = [expected_output]
		else:
			self.expected_output = expected_output

		self.runCommand()

		self.duration = timetools.Duration(self.end_time - self.start_time)
	
	def __str__(self):
		return self._terminal_string
	
	def runCommand(self):
		command_arguments = shlex.split(self.command)
		if any(not os.path.exists(fn) for fn in self.expected_output):

			#self._printCommand(command_arguments)
			process = subprocess.Popen(command_arguments, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			self.output = str(process.stdout.read(), 'utf-8')
		self.end_time = timetools.now()
		self.duration = timetools.Duration(self.end_time - self.start_time)
		self._showOutput(command_arguments)
		return self.output

	def _generateInputFileStatusString(self, arguments):
		string = "Input Files: \n"
		for arg in arguments:

			if isinstance(arg, str) and arg.startswith('/'):
				string += "{}\t{}\n".format(os.path.exists(arg), arg)

		return string

	def _showOutput(self, command_arguments):

		label_string = self.label
		command_string = self._generateCommandArgumentString(command_arguments)
		input_string = self._generateInputFileStatusString(command_arguments)
		status_string = self._generateTerminalStatusString()

		selected_output = list()
		if len(self.verbose) == 1 and 'all' in self.verbose:
			self.verbose = ['label', 'command', 'input', 'status', 'output']
		if 'label' in self.verbose:
			selected_output.append(label_string)
		if 'command' in self.verbose:
			selected_output.append(command_string)
		if 'input' in self.verbose:
			selected_output.append(input_string)
		if 'status' in self.verbose:
			selected_output.append(status_string)
		if 'output' in self.verbose:
			if  len(self.output) <= 300: #character limit
				selected_output.append("\tOutput:\n" + self.output)
			else:
				selected_output.append("\tOutput:\n" + self.output[:300])

		display_string = "\n".join(selected_output)

		if self.command_filename is not None:
			self.toFile(display_string, self.command_filename)

		if self.output_filename is not None:
			self.toFile(self.output, self.output_filename)

		if self.show_output:
			print(display_string)
			print(self.output)

		self._terminal_string = display_string

	def _generateTerminalStatusString(self):
		_status_string =  "\tTerminal Status:\n"
		for k, v in sorted(self.getStatus().items()):
			if k == 'outputFiles': continue
			if k == 'outputStatus': 
				_status_string += "\t\toutputStatus\n"
				for fns, fnf in v:
					_status_string += "\t\t\t{}\t{}\n".format(fns, fnf)
			else:
				_status_string += "\t\t{}\t{}\n".format(k,v)

		return _status_string

	def _generateCommandArgumentString(self, command_arguments):
		command_string = "\tCommand Arguments:\n"
		for argument in command_arguments:
			line = "\t{:<30}".format(argument)
			if argument.startswith('-'):
				line = "\n\t\t" + line

			command_string += line
		return command_string

	def getExpectedOutputString(self):
		if len(self.expected_output) > 0:
			expected_output_string = "\tExpected Output: \n"
			for eo in self.expected_output:
				line = "\t\t" + eo + "\n"
				expected_output_string += line
		else:
			expected_output_string = ""

		return expected_output_string

	@property
	def status(self):
		completed_successfully = all(os.path.exists(fn) for fn in self.expected_output)
		return completed_successfully

	def getStatus(self):
		""" The status of the terminal.
		"""
		self.end_time = timetools.now()
		self.duration = timetools.Duration(self.end_time - self.start_time)
		output_status = [(os.path.exists(fn), fn) for fn in self.expected_output]
		eo = self.expected_output[0] if len(self.expected_output) == 1 else self.expected_output
		status = {
			'status': 		self.status,
			'outputStatus': output_status,
			'startTime': 	self.start_time,
			'endTime': 		self.end_time,
			'duration': 	self.duration.isoFormat(),
			'outputFiles':  eo
		}

		return status
	@staticmethod
	def toFile(string, filename):
		try:
			with open(filename, 'a') as console_file:
				console_file.write(string)
		except Exception as exception:
			print("Could not write to the console file: ", str(exception))
			print(filename)