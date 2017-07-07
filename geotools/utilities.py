
import pandas
from unidecode import unidecode
import tabletools

####################################### Private Methods ############################################
def _isCode(string):
	""" Determines if a string represents a form of regional code """
	is_code = "-" in string
	is_code = is_code or any(c.isdigit() for c in string)
	is_code = is_code or not any(c.islower() for c in string)
	return is_code


def _convertToASCII(iterable, col = None):
	""" Converts a list of strings to a list of ascii strings. Non-string values
		are converted to an empty string.
		Parameters
		----------
			iterable: string, list<string>, pandas.Series, pandas.DataFrame
			col: string
				The column to use if the passed iterable is a dataframe.
		Returns
		-------
			result: list<string>
				A list of ASCII representations of the passed strings.
	"""
	if isinstance(iterable, str):
		iterable = [iterable]
	elif isinstance(iterable, pandas.DataFrame):
		iterable = iterable[col].values
	elif isinstance(iterable, pandas.Series):
		iterable = iterable.values
	iterable = [unidecode(s.strip() if isinstance(s, str) else "") for s in iterable]
	if len(iterable) == 1:
		iterable = iterable[0]
	return iterable

####################################### LOOKUP Methods ############################################
# Methods to match region names with region codes and vice versa


def findSimilarNames(code):
	""" Searches for similar ways of spelling the names
		of countries, states, or other regions.
		Parameters
		----------
			code: string [ISO-3 code]
	"""

	similar_names = {
	}

	similar_names = similar_names.get(code)
	return similar_names

####################################### Parsing Methods ############################################


def parseTable(io, column = "countryCode"):
	""" Loops through a table with either region codes or names
		and prints any missing names and/or codes.
		Parameters
		----------
			io: string, pandas.DataFrame, list<dict<>>
				Table to loop through.
			column: string
				The column to parse.
	"""
	table = tabletools.Table(io, skiprows = 1).df
	for index, row in table.iterrows():
		key_label = row[column]
		info = lookup(key_label)
		
		print(info['iso3Code'], '\t', info['countryName'])