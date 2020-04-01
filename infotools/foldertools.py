""" A collection of tools to inspect folders"""
from pathlib import Path
from typing import Dict

import pandas

from infotools import filetools


def get_filetypes(folder: Path, recursive: bool = True, byfiletype: bool = True) -> Dict[str, int]:
	""" Returns a dict with the number of each mimetype or filetype in the folder.
		Parameters
		----------
		folder: Path
			The folder to search through
		recursive: bool; default True
			Whether to look through files in all subfolders as well.
		byfiletype: bool; default True
			Whether to count files my filetype or mimetype
	"""
	if recursive:
		file_paths = [i for i in folder.glob("**/*") if i.is_file()]
	else:
		file_paths = [i for i in folder.iterdir() if i.is_file()]

	data = {'path': folder}
	for filename in file_paths:
		mtype, ftype = filetools.get_mimetype(filename)
		key = ftype if byfiletype else mtype
		data[key] = data.get(key, 0) + 1
	return data


def get_filetype_subfolders(folder: Path, recursive: bool = True, byfiletype: bool = True) -> pandas.DataFrame:
	""" Returns a table with the filetypes of each subfolder."""
	all_paths = list(folder.iterdir())
	subfolders = [i for i in all_paths if i.is_dir()]

	table = [get_filetypes(subfolder, recursive, byfiletype) for subfolder in subfolders]
	table.append(get_filetypes(folder, False, byfiletype))

	df = pandas.DataFrame(table)

	# There's no point in keeping the absolute path of each folder
	df['path'] = [i.stem for i in df['path'].values]

	# Use the `path` column as the index.
	df = df.set_index('path')
	# NaN values indicate that no files of that particular type were found in that folder.
	df = df.fillna(0)
	# Make sure each column is `int`, which is more consistent with the fact these are counts of objects.
	for column in df.columns:
		df[column] = df[column].astype(int)

	# Add a `total` column
	df['total'] = df.sum(axis = 1)

	# Sort by the total number of files.
	df = df.sort_values(by = 'total', ascending = False)

	return df



