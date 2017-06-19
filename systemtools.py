import os
import shlex
import subprocess
import psutil


def memoryUsage(show = True, units = 'MB'):
	""" Gets the current memory usage 
		Returns
		----------
			if show is False
			memory: int
				The total number of bytes being used by the current process
	"""

	process = psutil.Process(os.getpid())
	usage = process.memory_info().rss
	if show:
		if units == 'MB':
			value = usage / 1024**2
		else:
			value = usage
		print("Current memory usage: {0:.2f}{1}".format(value, units), flush = True)
	else:
		return usage

class Terminal:
    """ Wrapper around python system modules.
        Makes it easy to run a command and save any output.
    """
    def __init__(self, command, label = "", filename = None, show_output = False, use_system = False):
        self.label = label

        terminal_label = self._getCommandLabel(label)
        self.output = self._runCommand(command, terminal_label, use_system)
        if show_output:
            print(self.output)
        if filename is not None:
            self.updateConsoleLog(filename, command, self.output, label)

    @staticmethod
    def _getCommandLabel(label):
        if label == "": return label
        char = "#"
        max_len = 180
        edge = char * max_len
        edgelen = int(max_len/2 - int(len(label) / 2))
        middle = edgelen * char + label + edgelen*char

        return "\n".join([edge, middle, edge])

    @staticmethod
    def _runCommand(command, label, use_system = False):
        if label != "":
            print(label)
        if use_system:
            output = os.system(command)
        else:
            command = shlex.split(command)
            process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            output = str(process.stdout.read(), 'utf-8')
        return output

    @staticmethod
    def updateConsoleLog(filename, command, output, label = ""):
        """ Saves any text printed to the console to a file.
            Parameters
            ----------
            filename: string
                The file to save the text to.
            command: string
                The command that was executed.
            output: string
                The text that was printed to the terminal. Saved
                from process.stdout.read()
            label: string
                A string to write prior to writing the
                relevant text. Used to distinguish between
                different command that were executed.
        """

        if os.path.exists(filename): opentype = 'a'
        else: opentype = 'w'
        with open(filename, opentype) as console_file:
            console_file.write(label + '\n')
            console_file.write(' '.join(command) + '\n')
            console_file.write(output + '\n\n')

    def run(self, command, label, filename):
        pass
		self.command = command
		self.label = label
		self.filename = filename

		if expected_output is None:
			self.expected_output = []
		elif isinstance(expected_output, str):
			self.expected_output = [expected_output]
		else:
			self.expected_output = expected_output


		self.runCommand()

	def runCommand(self):
		if any(not os.path.exists(fn) for fn in self.expected_output):
			#self._printCommand(command_arguments)
			process = subprocess.Popen(command_arguments, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			self.output = str(process.stdout.read(), 'utf-8')
		else:
			self.output = ""



		command_string = "\tCommand Arguements:\n"
		for argument in command_arguments:
			line = "\t\t{:<30}".format(argument)
			if argument.startswith('-'):
				line = "\n" + line

			command_string += line

		if len(self.expected_output) > 0:
			expected_output_string = "\tExpected Output: \n"
			for eo in self.expected_output:
				expected_output_string += line
		else:
			expected_output_string = ""

		full_output_string = "\n".join([self.label, expected_output_string, command_string, self.output])

		if self.show_output:
			print(full_output_string)
			
		if self.filename is not None:
			with open(self.filename, 'a') as console_file:
				console_file.write(full_output_string)

	@property
	def status(self):
		files_missing = any(not os.path.exists(fn) for fn in self.expected_output)
		return not files_missing









