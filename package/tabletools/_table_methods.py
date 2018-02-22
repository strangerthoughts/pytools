
from .. import numbertools

import os
import pandas
import csv

def getTableType(io, **kwargs):
	""" Determines what the general layout of the
		table is based on the header.
		Parameters
		----------
			io: string, pandas.DataFrame, pandas.Series
			pandas keyword arguments are supported.
		Returns
		-------
			table_type: {'timeseries', 'verbose'}
				*'compact': The table is formatted with years
					as column names
				* 'long': Each variable in the table has its own row.
	"""
	if isinstance(io, str):
		table = Table(io, **kwargs)
		header = table.columns
	elif isinstance(io, pandas.DataFrame):
		header = io.columns
	else:
		header = io.index

	numeric_header = [i for i in header if numbertools.isNumber(i)]
	#static_header  = [i for i in header if i not in numeric_header]
	
	result = 'compact' if len(numeric_header) > 1 else 'long'
	return result


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
			'force': bool; default False
				If 'True', will return an empty list if the file does not exists.
		Returns
		-------
			reader: list<dict> or list<dict>, list<string>
				The contents of the file.
	"""
	fields = kwargs.get('fields', headers)
	delimiter = kwargs.get('delimiter', kwargs.get('sep', '\t'))
	force = kwargs.get('force', False)

	if os.path.exists(filename):
		with open(filename, 'r') as file1:
			reader = csv.DictReader(file1, delimiter = delimiter)
			fieldnames = reader.fieldnames
			reader = list(reader)
	elif force:
		reader = []
		fieldnames = []
	else:
		message = "tabletools.readCSV - The file does not exist: {}".format(filename)
		raise FileExistsError(message)

	if fields:
		return reader, fieldnames
	else:
		return reader


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
	if fieldnames is None: fieldnames = sorted(table[0].keys())
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
