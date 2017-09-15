
import pandas

from ._abstract_table import AbstractTable

DataFrameType = pandas.core.frame.DataFrame

class PandasTable(AbstractTable):
	"""
		Acts as a Pandas.DataFrame Emulator
	"""

	@property
	def df(self)->DataFrameType:
		return self._df

	@df.setter
	def df(self, value):
		pass
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
		self.df.sort_values(by = by, inplace = True, **kwargs)
		self.index_map = dict()

	def groupby(self, by):
		return self.df.groupby(by = by)
