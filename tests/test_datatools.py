from pathlib import Path
from infotools import datatools
import math
import pandas
def test_to_squareform():
	data = {
		('a', 'b'): 'ab',
		('b', 'c'): 'bc',
		('a', 'c'): 'ac'
	}

	expected = {
		'a': [math.nan, 'ab', 'ac'],
		'b': ['ab', math.nan, 'bc'],
		'c': ['ac', 'bc', math.nan]
	}
	expected = pandas.DataFrame(expected, index = ['a', 'b', 'c'])
	result = datatools.to_squareform(data)

	pandas.testing.assert_frame_equal(result, expected)