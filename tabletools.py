import filetools
import os
import pandas
import math

class Table:
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
	def __call__(self, on, where = None, column = None, value = None, flag = False):
		""" Parameters
			----------
				on: column label; default None
					The column to look in
				where: any; default None
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
				flag: bool; default False
					if passed to self.get_value(). If True, will return a 
					pandas.DataFrame object, else will return a pandas.Series
					object
			Notes
			----------
				If only 'on' is given, will return self.df[on]
				If 'on' and 'where' [and column] are given, will 
					return self.get_value(on, where, column, to_frame = flag)
				if on, where, column, and value are given, 
					calls self.put_value(on, where, column, value)
		"""
		if where is None:
			element = self.df[on]
		elif value is None:
			element = self.get_value(on, where, column, to_frame = flag)
		else:
			self.put_value(on, where, column, value)
			element = value

		#if isinstance(element, pandas.DataFrame) and len(element) == 1:
		#    element = element.iloc[0]
		#elif isinstance(element, pandas.Series) and len(element) == 1:
		#    element = element.iloc[0]
		return element

	def __iter__(self):
		for i in self.df.iterrows(): 
			yield i
	def __getitem__(self, index):
		#Try return self.df.__getitem__(index)
		return self.df.iloc[index]
	def __repr__(self):
		return "Database(source = {source}, shape = ({x}x{y}))".format(
			source = self.filename,
			x = len(self),
			y = len(self.df.columns))  
	def __str__(self):
		return self.__repr__()
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
			groups = self.df.groupby(on)
			self.index_map[on] = {key: group.index for key, group in groups}
		return self.index_map[on][where]
	
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
	def merge(self, right_df, left_on, right_on = None, how = 'left'):
		""" Merges a pandas.DataFrame object with the current database
			Parameters
			----------
				right_df: pandas.DataFrame
					The DataFrame to merge with the current database
				left_on: column label
					The column of the current database to merge on
				right_on: column label; default None
					The column of the passed DataFrame to merge on. If None, 
					will be equivilant to the value passed to right_on
				how:{'left', 'right', 'outer', 'inner'}; default 'left'
					* left: use only keys from the current database
					* right: use only keys from the passed DataFrame
					* outer: use union of keys from both sources
					* inner: use intersection of keys from both sources
			Returns
			----------
				function : None
		"""
		if isinstance(right_df, pandas.Series):
			raise ValueError("Cannot merge pandas.DataFrame and pandas.Series, use self.add_row() instead.")
		if right_on is None:
			right_on = left_on
		self.df = pandas.merge(self.df, right_df, how = how, left_on = left_on, 
			right_on = right_on, left_index = False, right_index = False)
	
	def head(self, rows = 5):
		return self.df.head(rows)   
	def info(self, verbose = True):
		print(self.df.info(verbose = verbose))
	def isin(self, on, value):
		""" Checks whether a value is in one of the database columns.
			Parameters
			----------
				on: column label
					The column to search in
				value:
					The value to search for
			Returns
			---------
				isin : bool
					Whether the selected value was found
		"""
		return value in self.df[on].values
	def items(self, *columns):
		""" Returns a generator that iterates over the selected columns
			Parameters
			----------
				*columns: string
					The columns to return
			Returns
			----------
				row: generator 
		"""
		columns_to_iterate = [self.df[column] for column in columns]
		for i, row in enumerate(zip(*columns_to_iterate)):
			yield row  
	def iteritems(self, *columns):
		""" Returns an indexed generator that iterates over the selected columns
			Parameters
			----------
				*columns: string
					The columns to return
			Returns
			----------
				row: index, generator 
		"""
		for index, row in enumerate(self.items(columns)):
			yield index, row
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
		if extension == '.xlsx':
			df = pandas.read_excel(filename, **kwargs)
		elif extension == '.pkl':
			df = pandas.read_pickle(filename)
		elif extension in ['.txt', '.csv', '.tsv']:
			sep = {'.txt':',', '.csv':',', '.tsv':'\t', 'fsv':'\f'}[extension]
			kwargs['delimiter'] = sep
			df = pandas.read_csv(filename, **kwargs)
		elif extension == '.db':
			df = pandas.read_sql(filename)
		else:
			raise NameError("{0} does not have a valid extension!".format(filename))
		return df
	def put_value(self, on, where, column, value, refresh_db = False):        
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
		if refresh_db: self.refresh()
	def get_value(self, on, where, column = None, to_frame = False):
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
				to_frame: bool; default False
					Whether to force the output to be pandas.DataFrame.
			Returns
			----------
				rows: pandas.Series, pandas.DataFrame
					The rows where the 'on' column contains the 'where'
					value. If a single row is found, it will be returned
					as a pandas.Series object.
		"""
		indices = self._get_indices(on, where)

		if column is None:
			return_this = self.df.loc[indices]
			if len(return_this) == 1:
				return_this = return_this.iloc[0]
		else:
			column_location = self.df.columns.get_loc(column)
			return_this = self.df.get_value(indices, column_location, takeable = True)
			if isinstance(return_this, numpy.ndarray):
				if len(return_this) == 1:
					return_this = return_this[0]
				else:
					return_this = pandas.Series(return_this, index = indices)
		if to_frame and isinstance(return_this, pandas.Series):
			return_this = return_this.to_frame().transpose()
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
	def random_value(self, on):
		""" Returns a random value from the selected column
			Parameters
			----------
				on: column label
					The column to choose a value from
			Returns
			----------
				value : scalar
					The value selected
		"""
		r = random.randrange(0, len(self.df))
		value = self.df[on].iloc[r]
		return value

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
	def save(self, filename, extension = None, na_rep = ''):
		""" Saves the database to the hdd
			Parameters
			----------
				filename: string
					The location on the disk to save the database to
					Supports .xlsx, .pkl, .csv, .db
				extension: string; default None
					Specifies the filetype to save the database as, 
					if different from the one given in filename
				na_rep: string, list-like; default ''
					The value to save nan values as. Currently non-working
			Returns
			---------
				function : None
		"""
		if extension is not None:
			filename = '.'.join(filename.split('.')[:-1] + [extension])

		if '.' not in filename:
			raise NameError("The file type was not specified!")
		
		file_format = filename.split('.').pop()
		if file_format == 'xlsx':
			self.df.to_excel(filename)
			
		elif file_format == 'pkl':
			self.df.to_pickle(filename)

		elif file_format == 'csv':
			self.df.to_csv(filename)

		elif file_format == 'db':
			from sqlalchemy import create_engine
			engine = create_engine('sqlite:///{0}'.format(filename))
			self.df.to_sql('Patient Database', engine)

		else:
			print("Could not save the database to", filename)
		print("Saved the database to", filename)
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
	def _boolselect(self, boolarray):
		return self.df[boolarray]
	def _set_dtype(self, column, dtype):
		self.df[column] = self.df[column].astype(dtype)
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

def isNull(value):
	if isinstance(value, str):
		return value == ""
	elif isinstance(value, float):
		return math.isnan(value)
	else:
		return value is None


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
	filename = "D:\\Proginoskes\\Documents\\Data\\Original Data\\United States\\Population\\Population Projections\\US State Population Projections.xlsx"
	static_columns = ['stateCode', 'stateName', 'report', 'source']
	new_filename = flattenTable(filename, static = static_columns)
	print(new_filename)