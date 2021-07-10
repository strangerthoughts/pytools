from pathlib import Path

from infotools import tabletools

folder_data = Path(__file__).parent / "data"


def test_read_table():
	""" Basically just tests if the function crashes when any table from the `data` folder is given to it.
	"""
	# ignore .txt file for now since they're not guaranteed to be tables.
	allowed_extensions = {'.csv', '.tsv', 'xls', 'xlsx', 'xlsm'}
	filenames = [i for i in folder_data.iterdir() if i.suffix in allowed_extensions]

	for filename in filenames:
		tabletools.read_table(filename)
