
from pathlib import Path
import pandas
def load_table(self, file_name: Path, **kwargs):
	""" Returns a dataframe of the suppled file
	"""
	extension = file_name.suffix
	default_args = {
		'.csv': {'delimiter': ','},
		'.tsv': {'delimiter': '\t'},
		'.fsv': {'delimiter': '\f'}
	}

	# arguments = self._cleanArguments(extension, arguments)
	file_name = str(file_name.absolute())
	if extension in {'.xls', '.xlsx', '.xlsm'}:

		df = pandas.read_excel(file_name, **kwargs)
	elif extension in {'.csv', '.tsv', '.fsv', '.txt'}:
		arguments = {**default_args.get(extension), **kwargs}
		if 'sheetname' in arguments: arguments.pop('sheetname')
		df = pandas.read_table(file_name, **arguments)
	elif extension == '.pkl':
		df = pandas.read_pickle(file_name)
	else:
		raise NameError("{} does not have a valid extension!".format(file_name))
	return df