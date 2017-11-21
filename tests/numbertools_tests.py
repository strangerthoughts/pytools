import unittest 
import datetime 
from ..numbertools import getBase, getMultiplier, humanReadable, isNumber, toNumber


class TestNumbertools(unittest.TestCase):
	def testGetBase(self):
		assert getBase(1000) == 'K'
		assert getBase(.00000000001) == 'n'
		assert getBase(0) == ''
	
	def testGetMultiplier(self):
		assert getMultiplier('n') == 1E-9
		assert getMultiplier('K') == 1000
		assert getMultiplier('T') == 1000000000000

	def testHumanReadable(self):
		#test basic cases
		value = 12345678901234567890
		assert humanReadable(1234.123) == '1.234123K'
		assert humanReadable(0.12345) == '123.45m'
		assert humanReadable(111222333444555) == '111.222333444555T'
		# test custom bases

		assert humanReadable(value, 'B') == '12345678901.234567890B'

	def testIsNumber(self):
		assert isNumber(123.456)
		assert isNumber('123.456')

	def testToNumber(self):
		assert toNumber('123.456')
		assert not toNumber('123..456')

		left = datetime.datetime(2017, 12, 31)
		right= datetime.datetime(2017, 1, 1)

		result = toNumber(left - right)
		
		assert result == 365.0

		

