import os
import pandas
#import time
import csv
from fuzzywuzzy import process
from unidecode import unidecode
from memory_profiler import profile
from pprint import pprint

from . import tabletools


####################################### Local Variables ############################################
LOCAL_PATH = os.path.dirname(__file__)
#SUBDIVISION_TABLE = pandas.read_excel(os.path.join(LOCAL_PATH, "data", "Subdivision ISO Codes.xlsx"))
#COUNTRY_TABLE = pandas.read_excel(os.path.join(LOCAL_PATH, "data", "country-codes.xlsx"))
SUBDIVISION_TABLE 	= tabletools.Table(os.path.join(LOCAL_PATH, "data", "Subdivision ISO Codes.xlsx"))
COUNTRY_TABLE 		= tabletools.Table(os.path.join(LOCAL_PATH, "data", "country-codes.xlsx"))


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
	return iterable
####################################### LOOKUP Methods ############################################
#Methods to match region names with region codes and vice versa
#countryName	englishName	officialName	iso2Code	iso3Code	currencyCode	currencyName	
#isIndependant	capitalName	continent	languages	geonameId
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
def lookup(label, **kwargs):
	""" Searches for a region code.
		Parameters
		----------
			label: string
				Name or iso3code for a country, state, or other region.
		Keyword Arguments
		-----------------
			'subcode': iso3 country code; default None
				Speeds up the search, if provided.
			'region_type': {'subdivisions', 'countries'}; default 'countries'
			'label_type': {'regionNames', 'regionCodes'}
				inferred if not provided. Labels containing numerical digits
				or a '-' character are assumed to be region codes.
	"""
	region_type = kwargs.get('region_type', 'countries')
	label_type = "regionCodes" if _isCode(label) else "regionNames"
	label_type = kwargs.get('label_type', label_type)
	subcode = kwargs.get('subcode')
	
	names = FILE_CACHE[region_type][label_type]
	if subcode is not None:
		super_regions = FILE_CACHE[region_type].get("contains", [])
		names = [s for c, s in zip(super_regions, names) if c == subcode]
	if label_type == "regionCodes":
		match = [i for i in names if i == label]
		if len(match) == 0:
			match = None
		else:
			match = match[0]
	else:
		match = process.extractOne(label, names)
		match, score = match
	if match is not None:
		index = FILE_CACHE[region_type][label_type].index(match)

		label_type = "regionNames" if label_type == "regionCodes" else "regionCodes"
		result = FILE_CACHE[region_type]["table"].iloc[index]
		result = result.to_dict()
	else:
		result = match
	return result

def lookupCountry(label, label_type = None):
	""" Matches a country's code or name.
		Parameters
		----------
			label: string
				A country's code or name.
			label_type: {'countryName', 'englishName', 'officialName', 'iso2Code',
						 'iso3Code', 'currencyCode', 'currencyName'}; default None
				The specific type and format of the identifier string that was passed.

		Returns
		-------
			result: dict<>
				* 'regionName': string
					The country's english name
				* 'regionCode': string
					The country's iso3Code
	"""
	label_is_code = _isCode(label)

	if label_type is None:
		label_type = 'iso3Code' if label_is_code else 'englishName'
	#print(label, label_type, label_is_code)

	match, score = process.extractOne(label, COUNTRY_TABLE.get_column(label_type))

	#Get the row from the table corresponding to the matched value
	result = COUNTRY_TABLE(label_type, match)
	result = result.to_dict()
	return result





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
			region_type: {"countries"}
	"""
	import tabletools
	table = tabletools.Table(io, skiprows = 1).df
	for index, row in table.iterrows():
		key_label = row[column]
		info = lookup(key_label)
		
		print(info['iso3Code'], '\t', info['countryName'])

####################################### Local Objects ############################################
#COUNTRY_TABLE.put_column('countryName', _convertToASCII(COUNTRY_TABLE.get_column('countryName')))
FILE_CACHE = {
	"subdivisions": {
		"table": 		SUBDIVISION_TABLE,
		"contains": 	_convertToASCII(SUBDIVISION_TABLE, "countryCode"),
		"regionCodes": 	_convertToASCII(SUBDIVISION_TABLE, "regionCode"),
		"regionNames":  _convertToASCII(SUBDIVISION_TABLE, "regionName")
	},
	"countries": {
		"table": 		COUNTRY_TABLE,
		"regionCodes": 	_convertToASCII(COUNTRY_TABLE, "iso3Code"),
		"regionNames": 	_convertToASCII(COUNTRY_TABLE, "englishName")
	}
}

if __name__ == "__main__":
	name = 'Argentina'

	pprint(lookupCountry(name))


	