import time
import random
from pprint import pprint
import numpy
import math


class Measurement:
	def __init__(self, x, y, durations):
		self.x = x
		self.y = y
		self.durations = durations

	def __str__(self):
		string = "Measurement(x = {}, y = {}, iterations = {}, {:.3E}±{:.3E}s)".format(
			self.x, self.y, len(self.durations), self.mean, self.std
		)
		return string

	@property
	def mean(self):
		return sum(self.durations) / len(self.durations)

	@property
	def std(self):
		avg = self.mean

		variance = sum([(i - avg) ** 2 for i in self.durations]) / (len(self.durations) - 1)
		deviation = math.sqrt(variance)
		return deviation

	def export(self):
		data = {
			'x': self.x,
			'y': self.y,
			'observations': len(self.durations),
			'mean': self.mean,
			'std': self.std,
			'nstd': numpy.std(self.durations)
		}
		return data


class Benchmarker:
	def __init__(self, functions, iterations, positional_arguments, keyword_arguments):
		for func in functions:
			for iteration in range(iterations):
				func(*positional_arguments, **keyword_arguments)


def benchmarkDict(func, power_range, bin_range, iterations):
	benchmarks = list()
	ms = list()
	for power in power_range:
		for category in bin_range:
			print("Running with power {} and category {}".format(power, category))
			values = [random.randint(0, category) for _ in range(10 ** power)]
			durations = list()
			for _ in range(iterations):
				start_time = time.time()
				func(values)
				duration = time.time() - start_time
				durations.append(duration)

			m = Measurement(power, category, durations)
			benchmarks.append(m)
	return benchmarks


def benchmark_dict_lookup(values):
	test_dict = dict()
	for i in values:
		if i not in test_dict:
			test_dict[i] = 0
		test_dict[i] += 1
	return test_dict


def benchmark_dict_exception(values):
	test_dict = dict()
	for i in values:
		try:
			test_dict[i] += 1
		except KeyError:
			test_dict[i] = 1
	return test_dict


def benchmark_dict_get(values):
	test_dict = dict()
	for i in values:
		test_dict[i] = test_dict.get(i, 0) + 1
	return test_dict


if __name__ == "__main__":
	import matplotlib.pyplot as plt

	power_range = list(range(4, 8))
	category_range = list(range(1024, 1025))
	iterations = 25

	lookup_results = benchmarkDict(benchmark_dict_lookup, power_range, category_range, iterations)
	exception_results = benchmarkDict(benchmark_dict_exception, power_range, category_range, iterations)
	get_results = benchmarkDict(benchmark_dict_get, power_range, category_range, iterations)
	print(benchmark_dict_exception.__name__)
	print(benchmark_dict_get.__name__)
	print(benchmark_dict_lookup.__name__)

	fig, ax = plt.subplots(figsize = (20, 10))
	ax.plot([i.x for i in lookup_results], [i.mean for i in lookup_results], color = 'r')
	ax.plot([i.x for i in exception_results], [i.mean for i in exception_results], color = 'g')
	ax.plot([i.x for i in get_results], [i.mean for i in get_results], color = 'b')

	plt.show()
