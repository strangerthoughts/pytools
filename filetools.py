
import csv
import hashlib
import os
import pandas
from pprint import pprint

def checkDir(path, full = False):
	""" Creates a folder if it doesn't already exist.
		Parameters
		----------
			path: string
				Path to a folder.
			full: bool; default False
				If true, will create any parent folders
				if they do not already exists.
		Returns
		-------
			status: bool
				Whether the folder was successfully created.
	"""

	if not os.path.exists(path):
		if full:
			os.makedirs(path)
		else:
			os.mkdir(path)

	return os.path.exists(path)


def generateFileMd5(filename, blocksize=2**20):
	""" Generates the md5sum of a file. Does
		not require a lot of memory.
		Parameters
		----------
			filename: string
				The file to generate the md5sum for.
			blocksize: int; default 2**20
				The amount of memory to use when
				generating the md5sum string.
		Returns
		-------
			md5sum: string
				The md5sum string.
	"""
	m = hashlib.md5()
	with open( filename , "rb" ) as f:
		while True:
			buf = f.read(blocksize)
			if not buf: break
			m.update( buf )
	return m.hexdigest()

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

def openTable(filename, **kwargs):
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
	basename, ext = os.path.splitext(filename)

	if ext in {'.xls', '.xlsx'}:
		data = pandas.read_excel(filename)
	
	elif ext in {'.csv', '.tsv'}:
		delimiter = '\t' if ext == '.tsv' else ','
		
		if return_type == 'dataframe':
			data = pandas.read_csv(filename, sep = delimiter)
		
		elif return_type == 'list':
			data, fieldnames = readCSV(
				filename, 
				sep = delimiter, 
				fields = True)
		else:
			message = "The variable 'return_type' has an unsupported_value: {0}".format(return_type)
	else:
		message = "The filename did not have a supported extension: '{0}'".format(ext)
		print(message)

	return data

def saveTable(table, filename, **kwargs):
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

def listAllFiles(folder):
	""" Lists all files in a folder. Includes subfolders.
		Parameters
		----------
			folder: string
				The folder to search through.
		Returns
		-------
			list<string>
				A list of all files that were found.
	"""
	file_list = list()
	for fn in os.listdir(folder):
		abs_path = os.path.join(folder, fn)
		if os.path.isdir(abs_path):
			file_list += listAllFiles(abs_path)
		elif os.path.isfile(abs_path): #Explicit check
			file_list.append(abs_path)
	return file_list


def searchForDuplicateFiles(folder, by = 'name'):
	""" Searches for duplicate files in a folder.
		Parameters
		----------
			folder: path
				The folder to search through. subfolders will be included.
			by: {'md5', 'name', 'size'}; default 'md5'
				The method to qualify two files as being the same.
		Return
		------
			duplicates: list<list<string>>
				A list of paired filenames representing identical files.
	"""
	all_files = listAllFiles(folder)

	checked_files = dict()
	_duplicate_keys = list()
	for filename in all_files:
		if by == 'md5':
			file_key = generateFileMd5(filename)
		elif by == 'name':
			file_key = os.path.basename(filename)
		elif by == 'size':
			file_key = os.path.getsize(filename)

		if file_key in checked_files:
			checked_files[file_key].append(filename)
			_duplicate_keys.append(file_key)
		else:
			checked_files[file_key] = [filename]
	_duplicates = list()
	for key in _duplicate_keys:
		_duplicates.append(checked_files[key])
	return _duplicates


if __name__ == "__main__":
	folder = "D:\\Proginoskes\\Documents\\Data\\table.tsv"

	#duplicates = searchForDuplicateFiles(folder)
	#pprint(duplicates)
	for key, value in sorted(os.environ.items()):
		print(key, value)