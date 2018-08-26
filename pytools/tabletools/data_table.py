"""
	Wrapper around pandas.DataFrame which offers convient functionality.
"""
import pandas
from pathlib import Path
from typing import List, Any, Union


class DataTable:
	"""

	"""

	def __init__(self, io, **kwargs):
		self.index_map = dict()
		self.df = self._parse_input(io, **kwargs)
		self._reset_index()

	def __getitem__(self, item):
		return self.df[item]

	def _parse_input(self, io, **kwargs) -> pandas.DataFrame:
		""" Parses the input to the Table constructor.

			Parameters
			----------
			io: str,Path, pandas.DataFrame, pandas.Series, list<dict<>>
				path to a file or folder with valid table files.

				other types will be passed to pandas.DataFrame()
		"""
		if isinstance(io, (str, Path)):
			self.filename = Path(io)
			table = self._load_from_path(self.filename, **kwargs)
		elif isinstance(io, pandas.DataFrame):
			table = io
		elif isinstance(io, list):
			table = pandas.DataFrame(io)
		else:
			try:
				table = pandas.DataFrame(io, **kwargs)
			except TypeError:
				try:
					print("Could not load the table, trying without keyword arguments.")
					table = pandas.DataFrame(io)
				except Exception as exception:
					message = "Could not load '{}' as a table.".format(str(io))
					print(message)
					raise exception

		return table

	def _load_from_path(self, io: Path, **kwargs) -> pandas.DataFrame:
		""" Loads a file. Acceptable keyword arguments will be passed to pandas.
			Parameters
			----------
				io: Path
					The database file. If a directory is given, will attempt to
					load all valid database files in the directory
					Available filetypes: .xlsx, .pkl, .csv, .db
			Returns
			----------
				self._load_file : pandas.DataFrame or dict(sheetname: pandas.DataFrame)
		"""
		if io.is_file():
			df = self._load_file(io, **kwargs)
		elif io.is_dir():  # path is a folder
			directory = io
			_load_dfs = list()
			for fname in directory.iterdir():
				if '~' in fname or fname.is_dir(): continue
				_load_dfs.append(self._load_file(fname, **kwargs))
			df = pandas.concat(_load_dfs)
		else:
			message = "The string passed to tabletools.DataTable() is not a valid filename or folder: {}".format(
				str(io))
			raise ValueError(message)

		return df

	@staticmethod
	def _load_file(file_name: Path, **kwargs) -> pandas.DataFrame:
		""" Returns a dataframe of the suppled file
		"""
		extension = file_name.suffix

		# arguments = self._cleanArguments(extension, arguments)
		file_name = str(file_name.absolute())
		if extension in {'.xls', '.xlsx', '.xlsm'}:
			df = pandas.read_excel(file_name, **kwargs)
		elif extension in {'.csv', '.tsv', '.fsv', '.txt'}:
			arguments = kwargs
			if 'sheetname' in arguments: arguments.pop('sheetname')
			df = pandas.read_table(file_name, **arguments)
		elif extension == '.pkl':
			df = pandas.read_pickle(file_name)
		else:
			raise NameError(f"{file_name} does not have a valid extension!")
		return df

	def _reset_index(self):
		""" Updates the sorted order and index of the database after changes
			are made
		"""
		self.df.reset_index(drop = True, inplace = True)
		self.index_map = dict()

	def _generate_index(self, column: str) -> pandas.Index:
		""" generates an index for all unique values in a column.
			Each key is a unique value present in the column, and each value is a list
			of the indices where that value is present.
		"""
		# New method, ~3s for 50k records.

		indexed_series = pandas.Index(self[column])
		return indexed_series

	def _get_indices(self, on: str, where: Any):
		""" Gets the row indices corresponding to rows with a value of
			'where' in column 'on'.
			Parameters
			----------
				on: column label
					The column to search
				where: scalar
					The value to find in column 'where'
			Returns
			----------
				self.index_map : pandas.Index
		"""

		return self.index_map[on].get_loc(where)

	def get_column(self, column: str, to_series: bool = False) -> Union[List, pandas.Series]:
		""" Retrieves all values in one of the database columns
			Parameters
			----------
				column: column label
					The column to retrieve
				to_series: bool; default False
					If true, returns a pandas.Series object rather than a numpy list.
			Returns
			----------
				column : numpy.ndarray
					The column values
		"""
		if to_series:
			column = self.df[column]
		else:
			column = list(self.df[column].values)
		return column

	def get_value(self, on: str, where: Any, column: str = None, **kwargs) -> Union[
		pandas.DataFrame, pandas.Series]:
		""" Retrieves a value from the database
			Parameters
			----------
				on: column label
					The column that contains the key value
				where: scalar
					The value to search the 'on' column for
				column: column label; default None
					The column with the return value. If not provided,
					returns all rows in the dataframe where the 'on'
					column contains the 'where' value.
			Keyword Arguments
			-----------------
				extract_one: bool; default False
					Whether to force the output to be pandas.DataFrame.
				default_value: None
			Returns
			----------
				pandas.Series, pandas.DataFrame
					The rows where the 'on' column contains the 'where'
					value. If a single row is found, it will be returned
					as a pandas.Series object.
		"""
		return_single_result = kwargs.get('extract_one', True)
		to_dataframe = kwargs.get('to_dataframe', False)
		indices = self._get_indices(on, where)

		if column is None:
			return_this = self.df.iloc[indices]
		else:
			return_this = self.df[column][indices]

		if return_single_result:
			pass

		if to_dataframe and not isinstance(return_this, pandas.DataFrame):
			if isinstance(return_this, pandas.Series):
				return_this = pandas.DataFrame([return_this])
			else:
				return_this = pandas.DataFrame(return_this)
		return return_this

	def melt(self, **kwargs):
		""""Unpivots" a DataFrame from wide format to long format, optionally leaving
			identifier variables set.

			Transforms a table from wide format to long format. Non-identifier columns
			will be merged together as paired 'subject' and 'value' columns.
			This function is useful to massage a DataFrame into a format where one
			or more columns are identifier variables (`id_vars`), while all other
			columns, considered measured variables (`value_vars`), are "unpivoted" to
			the row axis, leaving just two non-identifier columns, 'variable' and
			'value'.
			Keyword Arguments
			-----------------
			identifiers, id_vars : sequence of column names.
				Column(s) to use as identifier variables. These should be standardized
				ways of referring to an observation.
			to_file: bool, string; default None
				Whether to save the new table to a file. If a valid filename is passed,
				the table will be saved with that name. If 'to_file' is True and
				the table was originally loaded from a file (self.filename is defined),
				the table will be saved as basename + '.melt' + original_extension.
			variables, value_vars: sequence of column names; default None
				Column(s) to merge as 'variable'-'value' pairs. if not specified,
				all columns absent from the 'identifiers' sequence will be used.
			var_name : scalar; default 'variable'
				Name to use for the 'variable' column.
			value_name : scalar; default 'value'
				Name to use for the 'value' column.
		"""
		kwargs['id_vars'] = kwargs.get('identifiers', kwargs['id_vars'])
		kwargs['value_vars'] = kwargs.get('variables', kwargs.get('value_vars'))
		kwargs['var_name'] = kwargs.get('subjects', kwargs.get('var_name', 'variable'))
		kwargs['value_name'] = kwargs.get('values', kwargs.get('value_name', 'value'))
		kwargs['to_file'] = kwargs.get('to_file')

		new_table = pandas.melt(self.df, **kwargs)
		#new_table = self.fromDataframe(new_table)

		if kwargs['to_file']:
			if isinstance(kwargs['to_file'], str):
				fn = kwargs['to_file']
			else:
				fn = None  # No usable filename
			if fn:
				new_table.save(fn)

		return new_table

	def put_value(self, on: str, where: Any, column: str, value: Any):
		""" Parameters
			----------
				on: column label
					The column to search
				where: any
					The value to find in 'on'
				column: column label
					The column to modify
				value: any
					The new value to place in the selected column
			Returns
			-------
				value
		"""
		selected_indices = self._get_indices(on = on, where = where)
		column_index = self.df.columns.get_loc(column)
		self.df.set_value(
			selected_indices,
			column_index,
			value,
			takeable = True
		)

		return value

	def save(self, filename: Union[str, Path], **kwargs) -> Path:
		""" Saves the database. Keyword arguements will be passed to pandas.
			Parameters
			----------
				filename: string
					The location on the disk to save the database to
					Supports .xlsx, .pkl, .csv, .db
			Returns
			---------
			Path
				Path to the saved table.
		"""
		filename = Path(filename)
		sfilename = str(filename)  # Pandas doesn't work well with Paths yet.
		file_format = filename.suffix

		if file_format in {'.xls', '.xlsx'}:
			self.df.to_excel(sfilename, **kwargs)

		elif file_format == '.pkl':
			self.df.to_pickle(sfilename, **kwargs)

		elif file_format in {'.csv', '.tsv', '.fsv'}:
			if file_format == '.csv': sep = ','
			elif file_format == '.tsv': sep = '\t'
			else: sep = '\f'
			self.df.to_csv(sfilename, encoding = 'utf-8', sep = sep, **kwargs)

		else:
			print("ERROR: Could not save the database to", filename)
		return filename


if __name__ == "__main__":
	pass
