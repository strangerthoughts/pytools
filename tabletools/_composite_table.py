import os
import pandas
from typing import Generic
from ._pandas_table import PandasTable

DataFrameType = pandas.core.frame.DataFrame


class CompositeTable(PandasTable):
	""" Wrapper around a pandas.DataFrame object that allows convienient handling
		of tabular data. It is designed such that selection of row values based
		on other values is both fast and easy.

		Examples
		--------
			Example of iteration:
				for row in Table():
					pass
				
	"""
	def __init__(self, io, **kwargs):
		""" Parameters
			----------
				io: string, pandas.DataFrame, pandas.Series
					The database to load. If a directory is given,
					will load all valid files in that directory
			Keyword Arguments
			-----------------
				Any valid pandas keyword arguments are supported.qa 
				sheetname: string, int; default 0
					Indicates a specific sheet to load when loading
					an Excel spreadsheet
				
		"""
		kwargs['sheetname'] = kwargs.get('sheetname', 0)
		kwargs['skiprows'] = kwargs.get('skiprows')

		self.df = self._parseInput(io, **kwargs)
		self.original_indexer = kwargs.get('indexer', True)
		# Holds the indicies of specific groups within the database.
		# This is much faster than finding the indices on the fly
		self.index_map = dict()
		# Adds the index map and resets the index
		self._resetIndex()

	def __len__(self):
		""" Returns the number of rows present in the table. """
		return len(self.df)

	def __call__(self, on, where = None, column = None, value = None, **kwargs):
		""" Parameters
			----------
				on: column label, list<tuple<string:value>>
					The column to look in or a list of criteria to use
					when selecting rows.
				where: scalar
					The value to look for in the column indicated by on.
					If given, will find all rows with the value of 'where'
					in the column 'on'.
					If not given, will return the column indicated by on.
				column: column label; default None
					If given, will return the values in this column corresponding
					to the rows found with 'on' and 'where'
				value: any; default None
					If given, replaces the values in the columns of the rows
					found with 'on' and 'where'.
			Keyword Arguments
			-----------------
				single_value: bool; default True
					if passed to self.get_value(). If True, will return a 
					pandas.DataFrame object, else will return a pandas.Series
					object
				default: default None
					Value to return if the on/where/column criteria does not exist.
				'logic': {'and', 'or', 'not'}; default 'and'
					Used to select the logic when using chainselect()
				overwrite: bool; default False
					Prevents unintentional table modification. Must be set to 'True' 
					to modify a value in the table (by supplying 'value' with a value)
				to_dataframe: bool; default False
					If true, will always return a dataframe object. 
			Notes
			----------
				If only 'on' is given, will return self.df[on]
				If 'on' and 'where' [and column] are given, will 
					return self.get_value(on, where, column, to_frame = flag)
				if on, where, column, and value are given, 
					calls self.put_value(on, where, column, value)
		"""
		kwargs['extract_one'] = kwargs.get('extract_one', True)
		overwrite_value = kwargs.get('overwrite', False)
		ignore_errors = kwargs.get('ignore', False)
		kwargs['default'] = kwargs.get('default')

		try:
			
			if isinstance(on, list):
				# Assume chainSelect
				element = self.chainSelect(on, **kwargs)
			elif value is None:
				# Retrieve a specific column
				element = self.get_value(on, where, column, **kwargs)
			elif overwrite_value:
				# Replace a value
				element = self.put_value(on, where, column, value)
			else:
				message =  "The provided parameters to Table.__call__ are not valid: \n"
				message += "\ton = {},\n\twhere = {},\n\tcolumn = {},\n\tvalue = {}".format(
					on, where, column, value
				)
				raise ValueError(message)
		except KeyError as exception:
			print("Available Columns:")
			for col in self.columns:
				print('\t', col)
			if ignore_errors:
				element = None
			else:
				raise exception

		return element

	def __iter__(self):
		for i in self.iterrows(): 
			yield i[1]

	def __getitem__(self, index):
		
		return self.df.__getitem__(index)
	def __setitem__(self, key, value):
		self.df.__setitem__(key, value)
	def __str__(self):
		string = "Table(shape = ({x}x{y}))".format(
			x = len(self),
			y = len(self.columns)
		)  
		return string

	# Private Methods
	def _boolselect(self, boolarray):
		return self[boolarray]

	def _generate_index(self, column):
		""" generates an index for all unique values in a column.
			Each key is a unique value present in the column, and each value is a list
			of the indices where that value is present.
		"""
		# New method, ~3s for 50k records.
		indexed_series = dict()
		if self.original_indexer:
			for index, value in self[column].items():
				try:    
					indexed_series[value].append(index)
				except KeyError: 
					indexed_series[value] = [index]
			indexed_series = {k: pandas.Index(v) for k, v in indexed_series.items()}
		else:
			indexed_series = pandas.Index(self[column])
		return indexed_series

	def _get_indices(self, on, where):
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
		if on not in self.index_map.keys():
			indexed_series = self._generate_index(on)
			self.index_map[on] = indexed_series
		if self.original_indexer:
			return self.index_map[on][where]
		else:
			return self.index_map[on].get_loc(where)

	def _parseInput(self, io: Generic, **kwargs) -> DataFrameType:
		""" Parses the input to the Table constructor. 
			Parameters
			----------
				io: str, Table, pandas.DataFrame, list of dict
			
		"""

		if isinstance(io, str):
			table = self._load_file(io, **kwargs)

		elif isinstance(io, DataFrameType):
			table = io
		elif hasattr(io, 'toDataframe'):
			table = io.toDataframe()
		elif isinstance(io, list):
			table = pandas.DataFrame(io)
		else:
			raise Exception
		#else:
		#	try:
		#		table = pandas.DataFrame(io, **kwargs)
		#	except TypeError:
		#		try:
		#			print("Could not load the table, trying without keyword arguments.")
		#			table = pandas.DataFrame(io)
		#		except Exception as exception:
		#			message = "Could not load '{}' as a table.".format(str(io))
		##			raise exception

		return table


	@staticmethod
	def _reduceData(data):
		""" Transforms a dataframe/series/list into a single element if only one row in present. """
		if len(data.index) == 1:
			data = data.iloc[0]
		return data

	# Load and Save data to the filesystem

	@staticmethod
	def _load_file(filename:str, **kwargs) -> DataFrameType:
		""" Returns a dataframe of the suppled file. Any keyword arguments
			are passed on to pandas.
			Returns
			-------
				df: pandas.DataFrame
		"""
		extension = os.path.splitext(filename)[-1]

		if extension in {'.xls', '.xlsx', '.xlsm'}:
			_new_table = pandas.read_excel(filename, **kwargs)
		
		elif extension in {'.csv', '.tsv', '.fsv', 'txt'}:
			if 'sheetname' in kwargs: 
				kwargs.pop('sheetname')

			_new_table = pandas.read_table(filename, **kwargs)

		
		elif extension == '.pkl':
			_new_table = pandas.read_pickle(filename)
		else:
			raise NameError("{0} does not have a valid extension!".format(filename))
		assert isinstance(_new_table, pandas.DataFrame)
		return _new_table

	# Select data from the table
	def chainSelect(self, keys, extract_one = True, **kwargs):
		""" Retrieves data from the database based on several 
			different criteria.
			Parameters
			----------
				keys: list<tuple<string,value>>
					A list of key-value pairs specifing multiple columns
					and values to use a selection criteria.
					Ex. [(column1, value1), (column2, value2)] selects
					the rows where column1 contains value1 and column2 contains value2.
				extract_one: bool; default True
					If True, only the first result will be returned.
			Keyword Arguments
			-----------------
				'logic': {'and', 'or'}; default 'and'

		"""
		logic = kwargs.get('logic', 'and')
		return_single_result = extract_one
		boolindex = None
		for column, value in keys:
			indicies = self._get_indices(column, value)
			if boolindex is None:
				boolindex = indicies
			elif logic == 'and':
				boolindex = boolindex & indicies
			elif logic == 'or':
				boolindex = boolindex | indicies

		series = self.loc(boolindex)
		if return_single_result:
			series = self._reduceData(series)
		return series

	def get_value(self, on, where, column = None, **kwargs):
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
				rows: pandas.Series, pandas.DataFrame
					The rows where the 'on' column contains the 'where'
					value. If a single row is found, it will be returned
					as a pandas.Series object.
		"""
		return_single_result = kwargs.get('extract_one', True)
		to_dataframe = kwargs.get('to_dataframe', False)
		indices = self._get_indices(on, where)
		
		if self.original_indexer:
			if column is None:
				return_this = self.loc(indices)
			else:
				return_this = self[column].loc[indices]
		else:
			if column is None:
				return_this = self.iloc(indices)
			else:
				return_this = self[column][indices]

		if return_single_result:
			return_this = self._reduceData(return_this)

		if to_dataframe and not isinstance(return_this, pandas.DataFrame):
			if isinstance(return_this, pandas.Series):
				return_this = pandas.DataFrame([return_this])
			else:
				return_this = pandas.DataFrame(return_this)
		return return_this

	def get_column(self, column):
		""" Retrieves all values in one of the database columns
			Parameters
			----------
				column: column label
					The column to retrieve
			Returns
			----------
				column : numpy.ndarray
					The column values
		"""
		return self[column]

	def search(self, on, value, contains = True):
		""" Searches a column for a value and returns a DataFrame of every row
			where in the 'on' column contains the 'value' as a substring 
			Parameters
			----------
				on: column label
					The column to search
				value: string (substring)
					The string to search the 'on' column for. Finds all rows
					that contain the given value.
				contains: bool; default True
					If true, returns all rows that contains
					'value' as a substring, else returns all rows where
					'value' is not contained as a substring.
			Returns
			----------
				result : pandas.DataFrame
		"""
		if not isinstance(value, str):
			raise ValueError("{0} is not a string!".format(value))
		if contains:
			result = self[on].str.contains(value)
		else:
			result = ~self[on].str.contains(value)
		return self._boolselect(result)

	def select(self, on, where, comparison = '=='):
		""" Parameters
			----------
				on: column label
					The column to search
				where: scalar, list-like
					The value to search for in the 'on' column. If list-like,
					will return rows that contain any of the values given
				comparison: {'==', '!=', '>', '>=', '<', '<=', '~'}; default '=='
					Which comparison to use. If the 'where' variable is a list,
					the comparison will check if the values in the 'on' column
					are in the 'where' value (using comparison == '~' is the inverse).
			Returns
			----------
				result: pandas.Series or pandas.DataFrame
		"""
		if isinstance(where, (list, set)):
			elements = self[on].isin(where)
		elif comparison == '~':
			elements = ~self[on].isin(where)
		elif isinstance(where, pandas.Series):
			elements = where
		elif comparison == '==':
			elements = self[on] == where
		elif comparison == '!=':
			elements = self[on] != where
		elif comparison == '>':
			elements = self[on] > where
		elif comparison == '>=':
			elements = self[on] >= where
		elif comparison == '<':
			elements = self[on] < where
		elif comparison == '<=':
			elements = self[on] <= where
		else:
			message = "Improper comparison provided: '{}'".format(comparison)
			raise ValueError(message)
		result = self._boolselect(elements)

		return result

	# Manipulate attributes and data in the Table.
	def put_column(self, column, iterable):
		""" Inserts 'iterable' under column name 'column' """
		self[column] = iterable

	def put_value(self, on, where, column, value):
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
		column_index = self.columns.get_loc(column)
		self.set_value(
			selected_indices,
			column_index,
			value,
			takeable = True
		)

		return value

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
		kwargs['id_vars'] 	= kwargs.get('identifiers', kwargs['id_vars'])
		kwargs['value_vars']= kwargs.get('variables', 	kwargs.get('value_vars'))
		kwargs['var_name'] 	= kwargs.get('subjects', 	kwargs.get('var_name', 'variable'))
		kwargs['value_name']= kwargs.get('values', 		kwargs.get('value_name', 'value'))
		kwargs['to_file'] 	= kwargs.get('to_file')

		new_table = pandas.melt(self.df, **kwargs)


		if kwargs['to_file']:
			if isinstance(kwargs['to_file'], str):
				fn = kwargs['to_file']
			else: fn = None  # No usable filename
			if fn: 
				new_table.save(fn)

		return new_table

	def merge(self, other, **kwargs):
		""" Merges a pandas.DataFrame object with the current database. The
			default behavior is to merge the rows of 'other' that match a 
			specific key contained in the current table.
			General reference: https://pandas.pydata.org/pandas-docs/stable/merging.html
			Parameters
			----------
				other: pandas.DataFrame, tabletools.Table
					Another table to merge with this one.
			Keyword Arguments
			----------
				
				on, left_on, right_on: column label [REQUIRED]
					The column of the current database to merge on. If these are different,
					use 'right_on' and 'left' on to specify which columns to use.
				how:{'left', 'right', 'outer', 'inner'}; default 'left'
					* left: use only keys from the current database. Any rows in "other"
						that do not match any key in the current table will be discarded.
					* right: similar to 'left', but the other table will be used as the main table.
					* outer: use union of keys from both sources
					* inner: use intersection of keys from both sources
				inplace: bool; default False
					If true, The new table will replace the old one.
				sort : boolean, default False
					Sort the join keys lexicographically in the result DataFrame
				suffixes : 2-length sequence (tuple, list, ...); default ('_left', '_right')
					Suffix to apply to overlapping column names in the left and right
					side, respectively.
				copy : boolean, default True
					If False, do not copy data unnecessarily
				indicator : boolean or string, default False
					If True, adds a column to output DataFrame called "_merge" with
					information on the source of each row.
					If string, column with the same name will be added to the resulting table
					with information on source of which table the row originated from.
					Information column is Categorical-type and takes on a value of "left_only"
					for observations whose merge key only appears in 'left' DataFrame,
					"right_only" for observations whose merge key only appears in 'right'
					DataFrame, and "both" if the observation's merge key is found in both.
			Returns
			----------
				table: Table, None
					the merged table. If inplace = True, returns self instead.
		"""
		kwargs['how'] = kwargs.get('how', 'left')
		kwargs['suffixes'] = kwargs.get('suffixes', ('_left', '_right'))
		if 'on' not in kwargs and ('right_on' not in kwargs and 'left_on' not in kwargs):
			message = "Did not pass a column name to merge on."
			raise KeyError(message)

		if not isinstance(other, pandas.DataFrame): 
			other = other.toDataframe()

		new_df = pandas.merge(self.toDataframe, other, **kwargs)
		new_table = self.fromDataframe(new_df)
		return new_table
	
	
	# Methods based on the values contained in the table.
	def _fuzzySearch(self, value, column):
		""" Uses fuzzywuzzy to search for similar items in the selected column. """
		from fuzzywuzzy import process
		result = process.extractOne(value, self.get_column(column))
		return result

	def isin(self, value, column):
		""" Checks whether a value is in one of the database columns.
			Parameters
			----------
				value: scalar, iterable
					The value to search for.
				column: column-label
					The olumn to search in.
			Returns
			---------
				isin : bool
					Whether the selected value was found
		"""

		if isinstance(value, (list, set)):
			result = self[column].isin(value)
		else:
			result = value in self.get_column(column)
		return result



	def searchColumn(self, column, string):
		values = self.get_column(column)
		values = [i for i in values if isinstance(i, str) and string in i]
		return values
