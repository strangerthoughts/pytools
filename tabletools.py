import filetools
import os
import pandas
import math
import csv
from numpy import ndarray

class Table:
	""" Wrapper around a pandas.DataFrame object that allows convienient handling
		of tabular data.

		Examples
		--------
			iteration:
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
		self.use_old_index = kwargs.get('use_old_index', False)
		kwargs['sheetname'] = kwargs.get('sheetname', 0)
		kwargs['skiprows'] = kwargs.get('skiprows')

		if isinstance(io, pandas.DataFrame):
			self.df = io
			self.filename = 'Pandas.DataFrame'
		elif isinstance(io, str):
			self.df = self.load(io, **kwargs)
			self.filename = io
		elif isinstance(io, pandas.Series):
			self.df = io.to_frame().transpose()
			self.filename = 'Pandas.Series'
		else:
			obj_type = type(io)
			raise TypeError("The supplied data was of type({})".format(obj_type))

		#Holds the indicies of specific groups within the database.
		#This is much faster than finding the indices on the fly
		self.index_map = dict()
		#self.refresh()  
	def __len__(self):
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
				default_value: default None
					Value to return if the on/where/column criteria does not exist.
				overwrite: bool; default False
					Prevents unintentional table modification. Must be set to 'True' 
					to modify a value in the table (by supplying 'value' with a value)
			Notes
			----------
				If only 'on' is given, will return self.df[on]
				If 'on' and 'where' [and column] are given, will 
					return self.get_value(on, where, column, to_frame = flag)
				if on, where, column, and value are given, 
					calls self.put_value(on, where, column, value)
		"""
		kwargs['extract_one'] = kwargs.get('extract_one', True)
		if 'default_value' not in kwargs:
			kwargs['default_value'] = None
		if isinstance(on, list):
			#Assume chainSelect
			element = self.chainSelect(on, **kwargs)
		elif value is None:
			#Retrieve a specific column
			element = self.get_value(on, where, column, **kwargs)
		elif kwargs.get('overwrite', False):
			#Replace a value 
			element = self.put_value(on, where, column, value, **kwargs)

		return element

	def __iter__(self):
		for i in self.iterrows(): 
			yield i
	def __getitem__(self, index):
		#Try return self.df.__getitem__(index)
		return self.df.iloc[index]
	def __repr__(self):
		return "Table(source = {source}, shape = ({x}x{y}))".format(
			source = self.filename,
			x = len(self),
			y = len(self.df.columns))  
	def __str__(self):
		return self.__repr__()

	#Private Methods
	def _boolselect(self, boolarray):
		return self.df[boolarray]
	def _generate_index(self, column):
		#Switchable for debugging purposes.
		if self.use_old_index:
			#Old method, !7.7s for 50k records.
			groups = self.df.groupby(column)
			indexed_series = {key: group.index for key, group in groups}
		else:
			#New method, ~3s for 50k records.
			indexed_series = {}
			for index, value in self.df[column].items():
				try: 	indexed_series[value].append(index)
				except KeyError: indexed_series[value] = [index]
			indexed_series = {k:pandas.Index(v) for k, v in indexed_series.items()}
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

		return self.index_map[on][where]
	def _set_dtype(self, column, dtype):
		self.df[column] = self.df[column].astype(dtype)
	@staticmethod
	def _reduceData(data):
		""" Transforms a dataframe/series/list into a single element if only one row in present. """
		if len(data.index) == 1:
			data = data.iloc[0]
		return data
	#Load and Save data to the filesystem
	def load(self, io, **kwargs):
		""" Loads a file. Acceptable keyword arguments will be passed to pandas.
			Parameters
			----------
				io: string [PATH]
					The database file. If a directory is given, will attempt to
					load all valid database files in the directory
					Available filetypes: .xlsx, .pkl, .csv, .db
				ID: sheet name, sheet index; default 0
					The sheet to load (currently only works in Excel spreadsheets)
					To get a dict of dataframes for all sheets, pass 'all'
				na_values: list-like
					The values in io that indicate nan values
			Returns
			----------
				self._load_file : pandas.DataFrame or dict(sheetname: pandas.DataFrame)
		"""
		if os.path.isfile(io):
			df = self._load_file(io, **kwargs)
		else: #path is a folder
			directory = io
			_load_dfs = list()
			for fn in os.listdir(directory):
				if '~' in fn: continue
				filename = os.path.join(directory, fn)
				_load_dfs.append(self._load_file(filename, **kwargs))
			df = pandas.concat(_load_dfs)

		return df
	@staticmethod
	def _load_file(filename, **kwargs):
		""" Returns a dataframe of the suppled file
		"""
		extension = os.path.splitext(filename)[-1]
		if extension in {'.xlsx', '.xlsx'}:
			df = pandas.read_excel(filename, **kwargs)
		elif extension in {'.csv', '.tsv', '.fsv'}:
			if 'sheetname' in kwargs: kwargs.pop('sheetname')
			sep = {'.csv':',', '.tsv':'\t', '.fsv':'\f'}[extension]
			kwargs['delimiter'] = sep
			df = pandas.read_csv(filename, **kwargs)
		elif extension == '.txt':
			#Text file formatted as a table
			if 'sheetname' in kwargs: kwargs.pop('sheetname')
			df = pandas.read_table(filename, **kwargs)
		elif extension == '.pkl':
			df = pandas.read_pickle(filename)
		elif extension == '.db':
			df = pandas.read_sql(filename)
		else:
			raise NameError("{0} does not have a valid extension!".format(filename))
		return df
	def save(self, filename, **kwargs):
		""" Saves the database. Keyword arguements will be passed to pandas.
			Parameters
			----------
				filename: string
					The location on the disk to save the database to
					Supports .xlsx, .pkl, .csv, .db
			Returns
			---------
				function : None
		"""
		file_format = os.path.splitext(filename)[1]
		
		if file_format in {'.xls', '.xlsx'}:
			self.df.to_excel(filename)
			
		elif file_format == '.pkl':
			self.df.to_pickle(filename)

		elif file_format in {'.csv', '.tsv', '.fsv'}:
			if extension == '.csv': sep = ','
			elif extension == '.tsv': sep = '\t'
			elif extension == '.fsv': sep = '\f'
			self.df.to_csv(filename, encoding = 'utf-8', sep = sep)

		elif file_format == '.db':
			from sqlalchemy import create_engine
			engine = create_engine('sqlite:///{0}'.format(filename))
			self.df.to_sql('Patient Database', engine)

		else:
			print("ERROR: Could not save the database to", filename)
	
	#Index Rows from the table
	def lab(self, index):
		""" label-based indexing. labels may be numbers or strings.
			Parameters
			----------
				index: string, int
					The label of the rows to find
			Returns
			----------
				pandas.DataFrame.loc: DataFrame
		"""
		return self.df.loc[index]
	def pos(self, index):
		""" Positional-based indexing. Available values are in the range [0, len(self)).
			Parameters
			----------
				index: int
					The zero-based positional index of the rows to find
			Returns
			----------
				pandas.DataFrame.iloc: DataFrame
		"""
		return self.df.iloc[index]
	def ix(self, index):
		return self.df.ix[index]
	def concat(self, io):
		""" Adds a dataframe from a file to the existing internal dataframe
			Parameters
			----------
				io: string, pandas.DataFrame
					The database to add
			Returns
			----------
				function : None
		"""
		if isinstance(io, str):
			newdf = self.load(io)
		elif isinstance(io, pandas.DataFrame):
			newdf = io
		else:
			raise ValueError("{0} cannot be concatenated with the current DataFrame!".format(type(io)))
			   
		self.df = pandas.concat([self.df, newdf], ignore_index = True)
		self.refresh() 

	#Wrappers around commonly-used pandas methods.
	@property
	def columns(self):
		return self.df.columns
	def keys(self):
		return self.df.keys()
	def items(self):
		"""Iterator over (column name, Series) pairs."""
		for item in self.df.items():
			yield item
	def lookup(self, rows, columns):
		""" Label-based "fancy indexing" function for DataFrame.
    		Given equal-length arrays of row and column labels, return an
    		array of the values corresponding to each (row, col) pair.
    		rows must correspond to row indices.
		"""

		return self.df.lookup(rows, columns)
	def nlargest(self, n, column):
		""" Returns n rows in the table sorted by the largest values in 'column' """
		return self.df.nlargest(n, column)
	def nsmallest(self, n, column):
		""" Returns n rows in the table sorted by the smallest values in 'column' """
		return self.df.nsmallest(n, column)		
	def nunique(self, column):
		""" Returns a series object with the number of unique values in 'column'. index values
			are the unique values present in the column. """
		return self.df.nunique(column)
	def sort_values(self, by, **kwargs):
		self.df.sort_values(by = by, inplace = True)
		self.index_map = dict()
	def groupby(self, by):
		return self.df.groupby(by = by)
	def to_latex(self, **kwargs): return self.df.to_latex(**kwargs)
	#Select data from the table
	def chainSelect(self, keys, **kwargs):
		""" Retrieves data from the database based on several 
			different criteria.
			Parameters
			----------
				keys: list<tuple<string,value>>
					A list of key-value pairs specifing multiple columns
					and values to use a selection criteria.
					Ex. [(column1, value1), (column2, value2)] selects
					the rows where column1 contains value1 and column2 contains value2.
		"""
		return_single_result = kwargs.get('extract_one', True)
		boolindex = None
		for column, value in keys:
			indicies = self._get_indices(column, value)
			if boolindex is None:
				boolindex = indicies
			else:
				boolindex = boolindex & indicies

		series = self.df.loc[boolindex]
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
		indices = self._get_indices(on, where)
		
		if column is None:
			return_this = self.df.loc[indices]
		else:
			return_this = self.df[column].loc[indices]
		if return_single_result:
			return_this = self._reduceData(return_this)
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
		return self.df[column].values
	def getRandomValue(self, on):
		""" Returns a random value from the selected column
			Parameters
			----------
				on: column label
					The column to choose a value from.
			Returns
			----------
				value : scalar
					The value selected
		"""
		r = random.randrange(0, len(self.df))
		value = self.df[on].iloc[r]
		return value
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
			result = self.df[on].str.contains(value)
		else:
			result = ~self.df[on].str.contains(value)
		return self._boolselect(result)
	def select(self, on, where, comparison = '==', to_df = True):
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
				to_df: bool; True
					Determines whether to return a DataFrame
			Returns
			----------
				result: pandas.Series or pandas.DataFrame
		"""
		if isinstance(where, (list, set)):
			elements = self.df[on].isin(where)
		elif comparison == '~':
			elements = ~self.df[on].isin(where)
		elif isinstance(where, pandas.Series):
			elements = where
		elif comparison == '==':
			elements = self.df[on] == where
		elif comparison == '!=':
			elements = self.df[on] != where
		elif comparison == '>':
			elements = self.df[on] > where
		elif comparison == '>=':
			elements = self.df[on] >= where
		elif comparison == '<':
			elements = self.df[on] < where
		elif comparison == '<=':
			elements = self.df[on] <= where

		result = self._boolselect(elements)
		if not to_df:
			result = Database(result)
		return result


	#Manipulate attributes and data in the Table.
	def put_column(self, column, iterable):
		""" Inserts 'iterable' under column name 'column' """
		self.df[column] = iterable
	def put_value(self, on, where, column, value, **kwargs):
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
				refresh_db: bool; default False
					Whether to refresh the database after the value is changed
			Returns
			----------
			function: None
		"""
		selected_indices = self._get_indices(on = on, where = where)
		column_index = self.df.columns.get_loc(column)
		self.df.set_value(  selected_indices,
							column_index,
							value,
							takeable = True)
	def update(self, filename, on, change_column, change_values, dtypes = dict()):
		""" Loads an external database and updates the current database based on it
			Parameters
			----------
				filename: string
					The file with the updated values. Must be parsable by self.load()
				on: column label
					The column of the file that specifies the rows to change
				change_column: column label
					The column of the file that specifies the columns to change
				change_values: column label
					The column of the file that specifies the new values of 
					each row, column
				dtypes: dict; default dict()
					Specifies the datatypes of each column, to enforce
					homogeneity
		"""
		raise ValueError("Need to update this function so it works")
		updates = self.load(filename)

		for index, row in updates.iterrows():
			where = row[on]
			column = row[change_column]
			new_value = row[change_values]
			if column in dtypes.keys():
				if dtypes[column] == 'int':
					new_value = int(new_value)
				elif dtypes[column] == 'float':
					new_value = float(new_value)
				elif dtypes[column] == 'bool':
					new_value = bool(new_value)
				elif dtypes[column] == 'str':
					new_value = str(new_value)
			self.put_value(on = on, where = where, column = column, value = new_value)
	def add_row(self, *rows):
		""" Adds rows to the database
			Parameters
			----------
				*rows: dict, pandas.Series
					The rows to add.
			Returns
			----------
				function: None
		"""
		rows = [(pandas.Series(row) if isinstance(row, dict) else row) for row in rows]
		rows = [(row.to_frame().transpose() if isinstance(row, pandas.Series) else row)
					for row in rows]
		self.df = pandas.concat([self.df] + rows, ignore_index = False)
		self.refresh()
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
				function : None
		"""
		kwargs['how'] = kwargs.get('how', 'left')
		kwargs['suffixes'] = kwargs.get('suffixes', ('_left', '_right'))
		if 'on' not in kwargs and ('right_on' not in kwargs and 'left_on' not in kwargs):
			message = "Did not pass a column name to merge on."
			raise KeyError(message)

		if isinstance(other, Table): other = other.df

		if isinstance(right_df, pandas.Series):
			raise ValueError("Cannot merge pandas.DataFrame and pandas.Series, use self.add_row() instead.")
		if right_on is None:
			right_on = left_on
		new_df = pandas.merge(self.df, other, **kwargs)
		self.__init__(new_df)
	
	def refresh(self, sortby = None):
		""" Updates the sorted order and index of the database after changes
			are made
			Parameters
			----------
				None
			Returns
			----------
				function : None
		"""
		if sortby is not None:
			self.df.sort_values(by = self.sortby, inplace = True)
		self.df.reset_index(drop = True, inplace = True)  
		self.index_map = dict()
	def remove_columns(self, *columns):
		""" Removes the given columns
			Parameters
			----------
				*columns: column label
					The columns to delete
			Returns
			----------
				function : None
		"""
		for c in columns:
			if c in self.df.columns:
				del self.df[c]  
	def rename_column(self, column, label):
		""" Renames a column
			Parameters
			----------
				column: column label
					The column to rename
				label: column label
					The new name for the column
			Returns
			----------
				function : None
		"""
	
	#Methods based on the values contained in the table.
	def isin(self, value, column):
		""" Checks whether a value is in one of the database columns.
			Parameters
			----------
				value:
					The value to search for.
				column:
					The olumn to search in.
			Returns
			---------
				isin : bool
					Whether the selected value was found
		"""
		return value in self.get_column(column)

	#Methods for iterating through the items in the database.	

	def iterrows(self):
		""" Iterates over the rows in the table. The index is corresponds to
		the labeled index rather than the location (0-based) index.
		"""
		for index, row in self.df.iterrows():
			yield index, row

	#Show statistics and other information for the table.
	def head(self, rows = 5):
		return self.df.head(rows)   
	def info(self, verbose = True):
		print(self.df.info(verbose = verbose))
	def value_counts(self, column, sort = False):
		""" Wrapper for pandas.DataFrame.value_counts()
			Parameters
			----------
				column: column label
					The column to count unique values on
				sort: bool; default False
					Whether to sort the index of the returned data
			Returns
			----------
				series : pandas.Series
		"""
		series = self.df[column].value_counts() 
		if sorted: series = series.sort_index()
		return series	
	
	


def isNull(value):
	if isinstance(value, str):
		return value == ""
	elif isinstance(value, float):
		return math.isnan(value)
	else:
		return value is None

def getTableType(self, filename, skiprows = 0):
	""" Determines what the general layout of the
		table is based on the header.
		Parameters
		----------
			filename: string
			skiprows: int
		Returns
		-------
			table_type: {'timeseries', 'verbose'}
				*'timeseries': The table is formatted with years
					as column names
				* 'verbose': Each variable in the table has its own row.
	"""
	ext = os.path.splitext(filename)[-1]
	if ext == '.csv': delimiter = ','
	else: delimiter = '\t'

	with open(filename, 'r') as file1:
		while i < skiprows:
			file1.readline()
		header_line = file1.readline().strip() #removes the newline character at the end

	headers = header_line.split(delimiter)
	headers = [i for i in headers if i.isdigit()]



def flattenTable(filename, **kwargs):
	""" Flattens a dataset. The flattened dataset will
		automatically be saved as [basename].flattened.tsv.
		Parameters
		----------
			filename: string [PATH]
				A dataset formatted with variables
				as column names.
		Keyword Arguments
		-----------------
			'static': list<string, int> (list of column names); default []
				A list of columns to exclude from the
				flattening process. These columns will be
				included in the flattened dataset as additional columns.
				The following columns are automatically included:
					'baseYear'
					'regionCode'
					'regionName'
			'saveas': string [PATH]
				if provided, will save the flattened table with 
				the filename given to 'saveas'.
		Returns
		-------
			new_filename: string [PATH]
				The filename the table was saved to.
	"""
	basename, ext = os.path.splitext(filename)
	new_filename = kwargs.get('saveas', basename + '.flattened.tsv')
	static_columns = kwargs.get('static', [])
	static_columns += ['regionCode', 'regionName', 
		'source', 'url', 'baseDate', 'baseYear', 'customCode']
	
	data = filetools.openTable(filename, return_type = 'dataframe')
	table_columns = [i for i in data.columns if i not in static_columns]
	static_columns = [i for i in static_columns if i in data.columns]

	table = list()
	for index, row in data.iterrows():
		current_line = {c:row[c] for c in static_columns}
		for column in table_columns:
			current_value = row[column]
			if isNull(current_value): continue

			new_line = current_line.copy()
			new_line['subject'] = column
			new_line['value'] = current_value
			table.append(new_line)

	filetools.writeCSV(table, new_filename)

	return new_filename


def readCSV(filename, headers = False, **kwargs):
	""" Returns a csvfile as a list of dictionaries,
		where the csv header acts as the keys.
		Parameters
		----------
			filename: string
				Path to the file
			headers: bool; default False
				Whether to return the headers of the csv file as a list.
		Keyword Arguments
		-----------------
			'delimiter', 'sep': character; default '\t'
				The character that separated the fields in the csv file.
			'fields': bool; default False
				Whether to return the headers of the csv file as a list.
				identical to the 'headers' positional argument
		Returns
		-------
			reader: list<dict> or list<dict>, list<string>
				The contents of the file.
	"""
	fields = kwargs.get('fields', headers)
	delimiter = kwargs.get('delimiter', kwargs.get('sep', '\t'))

	if os.path.exists(filename):
		with open(filename, 'r') as file1:
			reader = csv.DictReader(file1, delimiter = delimiter)
			fieldnames = reader.fieldnames
			reader = list(reader)
	else:
		reader = []
		fieldnames = []

	if fields:
		return reader, fieldnames
	else:
		return reader

def readTable(filename, **kwargs):
	""" Reads a file and returns an appropriate data type.
		Parameters
		----------
			filename: string
				Path to a file.
		Keyword Arguments
		-----------------
			'return_type': {'dataframe', 'list'}; default 'dataframe'
			'skiprows': int; default 0
				The number of rows to skip.
	"""
	return_type = kwargs.get('return_type', 'dataframe')
	skiprows = kwargs.get('skiprows', 0)


		

	return data

def writeTable(table, filename, **kwargs):
	""" Saves a table to a file. The filetype will 
		be determined from the extension.
		Parameters
		----------
			table: list<dict<>>
				The table to save.
			filename: string
				Path to the file that will be saved.
		Keyword Arguments
		-----------------
			'append': bool; default True
				Whether to overwrite a file, if it already exists.
		Returns
		-------
			filename: string
				The filename that the table was saved to.
	"""

	ext = os.path.splitext(filename)
	if ext in {'.xls', 'xlsx'}:
		#Will probably use pandas.
		pass
	elif ext in {'.csv', '.tsv'}:
		writeCSV(table, filename, **kwargs)

	return filename

def writeCSV(table, filename, **kwargs):
	""" Writes a csv file from a list of dictionaries.
		Parameters
		----------
			table: list<dict>
				The table to write to the file.
			filename: string [PATH]
				The file to write.
		Keyword Arguments
		-----------------
			'delimiter', 'sep': character
				The character to separate each field with.
			'empty', 'restval': string; default ""
				The value to use for rows with missing values.
			'fields', 'fieldnames': list<string>; default None
				The fieldnames to use. If none are provided, the
				sorted keys of the first element in the table
				will be used.
			'append': bool; default False
				If true, will append the table to an existing
				file rather than overwriting any existing one.
	"""
	if len(table) == 0: return None
	fieldnames = kwargs.get('fieldnames', kwargs.get('fields'))
	if fieldnames is None:fieldnames = sorted(table[0].keys())
	opentype = 'a' if kwargs.get('append', False) else 'w'
	delimiter = kwargs.get('delimiter', kwargs.get('sep', '\t'))
	empty_value = kwargs.get('empty', kwargs.get('restval', ""))
	
	with open(filename, opentype, newline = "") as csv_file:
		writer = csv.DictWriter(
			csv_file, 
			delimiter = delimiter, 
			fieldnames = fieldnames,
			restval = empty_value)
		if opentype != 'a' or os.path.getsize(filename) == 0:
			writer.writeheader()

		writer.writerows(table)

	return filename


if __name__ == "__main__":
	filename = os.path.join(os.getcwd(), 'data', "country-codes.xlsx")
	df = Table(filename)
	for row in df:
		print(row['iso3Code'])