import itertools
from typing import *

import pandas


def to_squareform(pairwise_values: Dict[Tuple[str,str], Any], default:Any = None)->pandas.DataFrame:
	"""
		Converts a dictionary of pariwise values (ex. a representation of pairwise distances)
		into a square matrix, where the keys in the labels are converted
		to columns and index labels.
		Ex.
		data = {
			('a', 'b'): 'ab',
			('b', 'c'): 'bc',
			('a', 'c'): 'ac'
		}
		matrix:
			'a'	'b'	'c'
		'a'	None	'ab'	'ac'
		'b'	'ab'	None	'bc'
		'c'	'ac'	'bc'	None
	"""

	keys = sorted(set(itertools.chain.from_iterable(pairwise_values)))
	_square_map = dict()
	for left in keys:
		series = dict()
		for right in keys:
			value = pairwise_values.get((left, right))
			if value is None:
				value = pairwise_values.get((right, left), default)
			series[right] = value
		_square_map[left] = series
	return pandas.DataFrame(_square_map)
