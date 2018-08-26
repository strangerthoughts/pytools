from fuzzywuzzy import fuzz
import textdistance
from typing import *
from pprint import pprint
import pandas

if __name__ == "__main__":


	dictionary: List[str] = ['new york', 'new york city']
	combinations = list()
	function_names = [i for i in dir(textdistance) if callable(getattr(textdistance, i))]


	for left in dictionary:
		for right in dictionary:
			if left == right: continue
			combinations.append((left, right))
	print(combinations)
	table = list()
	seen = set()
	for left, right in combinations:
		if (left, right) in seen or (right, left) in seen: continue
		seen.add((left, right))
		fuzzy_ratio = fuzz.ratio(left, right)
		fuzzy_partial_ratio = fuzz.partial_ratio(left, right)
		row = {
			'left':              left,
			'right':             right,
			'fuzzyRatio':        fuzzy_ratio,
			'fuzzyPartialRatio': fuzzy_partial_ratio
		}
		for function_name in function_names:
			function = getattr(textdistance, function_name)
			try:
				result = function(left, right).distance()
			except:
				continue


			row[function_name] = result
		table.append(row)

		table = pandas.DataFrame(table)
		print(table)

