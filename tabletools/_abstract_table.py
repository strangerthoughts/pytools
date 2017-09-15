import os

import pandas

DataFrameType = pandas.core.frame.DataFrame
class AbstractTable:

	@classmethod
	def fromDataframe(cls, io, **kwargs):
		""" Returns a new Table object from a pandas.DataFrame object.
			Keyword arguments are passed on to the Table constructor.
			Parameters
			----------
				io: pandas.DataFrame
					The input dataframe
			
		"""
		return cls(io, **kwargs)
	
	@classmethod
	def fromList(cls, io):
		""" Creates a table from a list of dictionaries.
			Parameters
			----------
				io: list<dict<>>
					A list of dictionaries to convert to a table.
		"""

		df = pandas.DataFrame(io)
		
		return df

	def toDataframe(self):
		return self.df

	@property
	def df(self) -> DataFrameType:
		return self._df

	@df.setter 
	def df(self, value:DataFrameType):
		assert isinstance(value, pandas.DataFrame)
		self._df = value

	@property 
	def columns(self):
		return self._df.column
	
	def loc(self, index):
		return self._df.loc[index]
	def iloc(self, index):
		return self._df.iloc[index]

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
		_current_table = self._df

		if file_format in {'.xls', '.xlsx'}:
			_current_table.to_excel(filename, **kwargs)
			
		elif file_format == '.pkl':
			_current_table.to_pickle(filename, **kwargs)

		elif file_format in {'.csv', '.tsv', '.fsv'}:
			if file_format == '.csv': 
				sep = ','
			elif file_format == '.tsv': 
				sep = '\t'
			else: 
				sep = '\f'
			_current_table.to_csv(filename, encoding = 'utf-8', sep = sep, **kwargs)

		else:
			print("ERROR: Could not save the database to", filename)

	def _resetIndex(self):
		""" Updates the sorted order and index of the database after changes
			are made
		"""
		self._df.reset_index(drop = True, inplace = True)
		self.index_map = dict()
	def set_value(self, *args, **kwargs):
		self._df.set_value(*args, **kwargs)

	def iterrows(self):
		""" Iterates over the rows in the table. The index is corresponds to
		the labeled index rather than the location (0-based) index.
		"""
		for index, row in self._df.iterrows():
			yield index, row 
