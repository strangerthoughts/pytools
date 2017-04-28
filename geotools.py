import os
import pandas
#import time
import csv
from fuzzywuzzy import process
from unidecode import unidecode
from memory_profiler import profile
from pprint import pprint
SUBDIVISION_TABLE = pandas.read_excel("data/Subdivision ISO Codes.xlsx")
COUNTRY_TABLE = pandas.read_excel("data/country-codes.xlsx")

def decodeList(iterable, col = None):
	""" Converts a list of strings to a list of ascii strings.
		Parameters
		----------
			iterable: list<string>, pandas.Series
			col: string
				required if the iterable is a dataframe
	"""
	if isinstance(iterable, pandas.DataFrame):
		iterable = iterable[col]
	if isinstance(iterable, pandas.Series):
		iterable = iterable.values
	iterable = [unidecode(s.strip() if isinstance(s, str) else "") for s in iterable]
	return iterable

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
def _isCode(string):
	""" Determines if a string represents a form of regional code """
	tests = [
		"-" in string,
		not any(c.isdigit() for c in string),
		string.isupper()
	]
	is_code = any(tests)
	return is_code
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


FILE_CACHE = {
	"subdivisions": {
		"table": 		SUBDIVISION_TABLE,
		"contains": 	decodeList(SUBDIVISION_TABLE, "countryCode"),
		"regionCodes": 	decodeList(SUBDIVISION_TABLE, "regionCode"),
		"regionNames":  decodeList(SUBDIVISION_TABLE, "regionName")
	},
	"countries": {
		"table": 		COUNTRY_TABLE,
		"regionCodes": 	decodeList(COUNTRY_TABLE, "iso3Code"),
		"regionNames": 	decodeList(COUNTRY_TABLE, "englishName")
	}
}

if __name__ == "__main__":
	filename = "D:\\Proginoskes\\Documents\\Data\\Original Data\\World\\International Tourism\\Tourists.xlsx"

	parseTable(filename, column = 'Country Code')


	