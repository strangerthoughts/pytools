import collections
from pprint import pprint
import math

class NumberList(collections.UserList):
	def __init__(self, *args):
		super().__init__(self)
	def getValue(self, index):
		try:
			element = self[index]
		except IndexError:
			element = None
		return element

	def first(self):
		return self.getValue(0)

	def last(self):
		return self.getValue(-1)

	def mean(self):
		if len(self) == 0:
			average = 0
		else:
			average = sum(self) / len(self)
		return average

	def median(self):
		raise NotImplementedError


	def std(self):
		avg = self.mean

		variance = sum([(i - avg) ** 2 for i in self]) / (len(self) - 1)
		deviation = math.sqrt(variance)
		return deviation

	def countValues(self):
		return collections.Counter(self)

	@property
	def values(self):
		return NumberList(sorted(self))


if __name__ == "__main__":
	array = NumberList([1, 2, 3, 4, 5, 5, 4, 3, 2, 2, 3, 4, 7])
	print("Mean: ", array.mean())
	#print("Median: ", array.median())
	pprint(array.countValues())
