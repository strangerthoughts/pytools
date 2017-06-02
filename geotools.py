import os
import pandas
from fuzzywuzzy import fuzz
from unidecode import unidecode
import tabletools


####################################### Local Variables ############################################
LOCAL_PATH = os.path.dirname(__file__)

SUBDIVISION_TABLE = tabletools.Table(os.path.join(LOCAL_PATH, "data", "Subdivision ISO Codes.xlsx"))
COUNTRY_TABLE     = tabletools.Table(os.path.join(LOCAL_PATH, "data",         "country-codes.xlsx"))


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


class LookupRegionCode:
    def __init__(self):
        self.column_cache = dict()

    def __call__(self, label, kind = "country", label_type = None):
        if label_type is None:
            label_type = self._checkIfStringIsCode(label)
        kind = 'countries' if kind == 'country' else 'regions'
        result = self._searchTable(label, label_type, kind)
        return result
    @staticmethod
    def _checkIfStringIsCode(string):
        contains_code_characters = '-' in string and " " not in string
        is_short = len(string) < 4
        is_uppercase = string.isupper()

        is_code = (contains_code_characters and is_uppercase) or is_short
        
        if not is_code:         label_type = 'countryName'
        elif len(string) == 2:  label_type = 'iso2Code'
        elif len(string) == 3:  label_type = 'iso3Code'
        else:                   
            print(string)
            print('-' in string)
            print(not " " in string)
            label_type = 'regionCode'

        return label_type
    
    def _getTableColumn(self, table_name, column):
        """ Saves the ASCII version of each column to save time """
        if table_name not in self.column_cache:
            self.column_cache[table_name] = dict()
        if column not in self.column_cache[table_name]:
            _col = FILE_CACHE[table_name]['table'].get_column(column, True)
            _col = dict(zip(_col.keys(), _convertToASCII(_col.values)))
            self.column_cache[table_name][column] = _col
        return self.column_cache[table_name][column]

    @staticmethod
    def _getTableSettings(label_type):
        use_fuzzysearch = False
        if label_type == 'countryName':
            columns = ['regionName', 'officialEnglishName', 'otherNames']
            use_fuzzysearch = True
        elif label_type == 'regionName':
            columns = ['regionName']
            use_fuzzysearch = True
        elif label_type == 'iso3Code' or label_type == 'isoCode':
            columns = ['iso3Code']
        elif label_type == 'iso2Code':
            columns = ['iso2Code']
        elif label_type == 'regionCode':
            columns = ['regionCode']
        else:
            message = "Not a valid region identifier: {}".format(label_type)
            raise ValueError(message)

        settings = {
            'columns': columns,
            'fuzzy': use_fuzzysearch
        }
        return settings

    @staticmethod
    def _searchColumn(search_term, column, fuzzy = False):
        if fuzzy:
            candidates = list()
            found_match = False
            for index, value in column.items():
                score = fuzz.token_sort_ratio(search_term, value)
                if score >= 90: 
                    candidates.append((index, value, score))
                    found_match = True

            if found_match:
                value = max(candidates, key = lambda s: s[-1])
                index = value[0]
            else:
                index = None

        else:
            try:
                index = column.index(search_term)
                found_match = True
            except IndexError:
                index = None
                found_match = False

        result = {
            'index': index,
            'match': found_match
        }
        return result

    def _searchTable(self, label, label_type, table_name):
        label = _convertToASCII(label)
        current_table = FILE_CACHE[table_name]['table']
        settings = self._getTableSettings(label_type)
        columns = settings['columns']
        use_fuzzysearch = settings['fuzzy']

        for column in columns:
            column_values = self._getTableColumn(table_name, column)

            result = self._searchColumn(label, column_values, use_fuzzysearch)

            if result['match']:
                index = result['index']
                region_information = current_table.ix(index)
                break
        else:
            region_information = None

        return region_information


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

####################################### Local Objects ############################################


FILE_CACHE = {
    "regions": {
        "table":        SUBDIVISION_TABLE,
        "contains":     _convertToASCII(SUBDIVISION_TABLE, "countryCode"),
        "regionCodes":  _convertToASCII(SUBDIVISION_TABLE, "regionCode"),
        "regionNames":  _convertToASCII(SUBDIVISION_TABLE, "regionName")
    },
    "countries": {
        "table":        COUNTRY_TABLE,
        "regionCodes":  _convertToASCII(COUNTRY_TABLE, "iso3Code"),
        "regionNames":  _convertToASCII(COUNTRY_TABLE, "englishName")
    }
}

lookup = LookupRegionCode()

def test1():
    filename = "C:\\Users\\Deitrickc\\Google Drive\\Harmonized Data\\World\\Annual_Exchange_Rates.xls"
    table = tabletools.Table(filename, sheetname = 0)
    for index, row in table:
        country_name = row['countryName']
        result = lookup(country_name)

        if result is not None:
            print("{}\t{}".format(result['regionName'], result['iso3Code']))
        else:
            print(country_name)


if __name__ == "__main__":
    test1()

