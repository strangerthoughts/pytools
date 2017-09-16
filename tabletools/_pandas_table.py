
from ._composite_table import CompositeTable


class PandasTable(CompositeTable):
	"""
		Temporary functions
		abs()
	"""
	@property
	def columns(self):
		return self.df.columns

	def abs(self, column = None):
		""" Returns a Table with all numeric values converted to
			the absolute value of themselves.
			Parameters
			----------
				column: column-label
					If provided, only the selected column will be converted.
		"""
		if column:
			result = self.df
			result[column] = result[column].abs()
		else:
			result = self.df.abs()
		return result

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

	def to_latex(self, **kwargs): return self.df.to_latex(**kwargs)
