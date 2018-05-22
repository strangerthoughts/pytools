from pytools import tabletools

import unittest
import os
from pathlib import Path
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'test_data')
basename = os.path.join(DATA_FOLDER, 'Annual State Populations')
class TestDatabase(unittest.TestCase):
	def test_read_csv(self):
		fname = basename + '.csv'
		table = tabletools.Table(fname)
	def test_read_tsv(self):
		fname = basename + '.tsv'
		table = tabletools.Table(fname)
	def test_read_xls(self):
		fname = basename + '.xls'
		table = tabletools.Table(fname)
	def test_read_xlsx(self):
		fname = basename + '.xlsx'
		table = tabletools.Table(fname)
	def test_read_csv_with_kwargs(self):
		pass
	def test_read_xlsx_with_kwargs(self):
		pass

	def test_read_from_pathlib(self):
		filename = Path(basename).with_suffix('.xlsx')
		table = tabletools.Table(filename)

if __name__ == "__main__":
	unittest.main()
