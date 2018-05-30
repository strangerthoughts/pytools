import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from typing import *
from pytools import numbertools
from numbers import Number

SeriesType = List[Tuple[Number, Number]]

plt.style.use('fivethirtyeight')
class Plot:
	def __init__(self, x: SeriesType, y:Optional[SeriesType]=None, **kwargs):
		self._series_variables = dict()
		kwargs = self._getDefaultKeywordArguments(kwargs)
		self.options = kwargs
		self._createInitialPlot()

		self.addLabels(**kwargs)

		self.addSeries(x, y, **kwargs)


	def _createInitialPlot(self) -> None:
		# Holds keyword arguments for every series.
		self.data = dict()

		def formatter(x, pos):
			return numbertools.human_readable(x, precision = 1)

		# The basic plots
		self.figure, self.chart = plt.subplots(figsize = self.options['figsize'])
		self.chart.yaxis.set_major_formatter(tkr.FuncFormatter(formatter))

	@staticmethod
	def _getDefaultKeywordArguments(kwargs: Dict) -> Dict:
		kwargs['figsize'] = kwargs.get('figsize', (20, 10))
		kwargs['style'] = kwargs.get('style', 'fivethirtyeight')
		return kwargs

	def addLabels(self, **kwargs) -> None:
		""" labels various parts of the map.
			Keyword Arguments
			-----------------
				title: string
					The title of the plot
				xlabel: string
				ylabel: string
		"""

		if 'title' in kwargs:
			self.figure.suptitle(kwargs['title'])
		if 'xlabel' in kwargs:
			plt.xlabel(kwargs['xlabel'])
		if 'ylabel' in kwargs:
			plt.ylabel(kwargs['ylabel'])

	def addLegend(self, kwargs):
		pass

	def addSeries(self, x: SeriesType, y: Optional[SeriesType] = None, **kwargs):
		""" Adds a set of x and y value pairs to the plot.
			Parameters
			----------
			x: list<number,number>, list<number>
				With the full set of x-y pairs or the x values to plot.
			y: list<number>
				Only needed if 'x' only contains the x values.
			Keyword Arguments
			-----------------
				'x', 'y': list<number> [Required if 'series' is None and 'y' is given]
					x-values to pair with the additional 'y' keyword.
				color: string
					The desired color for the series.
				label: string
					name of the series. if absent, a name will automatically be generated.
		"""
		if y is None:
			x, y = zip(*x)

		label = kwargs.get('label', self._generateSeriesLabel())
		color = kwargs.get('color', self._generateSeriesColor())

		self.chart.scatter(x = x, y = y, c = color, label = label)

	@staticmethod
	def render(filename: str = None):
		""" Renders the plot """
		if filename is None:
			plt.show()

	@staticmethod
	def _generateSeriesColor() -> str:
		color = "#AA5588"
		return color

	def _generateSeriesLabel(self) -> str:
		""" Automatically generates a label for a series based on the number
			of previously generated plots.
		"""

		_series_index = len(self._series_variables.keys()) + 1
		label = "series{0}".format(_series_index)
		return label


if __name__ == "__main__":
	data = [
		(1800, 79216),
		(1810, 119734),
		(1820, 152056),
		(1830, 242278),
		(1840, 391114),
		(1850, 696115),
		(1860, 1174779),
		(1870, 1478103),
		(1880, 1911698),
		(1890, 2507414),
		(1900, 3437202),
		(1910, 4766883),
		(1920, 5620048),
		(1930, 6930446),
		(1940, 7454995),
		(1950, 7891957),
		(1960, 7781984),
		(1970, 7894862),
		(1980, 7071639),
		(1990, 7322564),
		(2000, 8008278),
		(2010, 8175133),
		(2016, 8537673)
	]
	title = 'New York City Population'
	x_label = 'year'
	y_label = 'population'

	chart = Plot(data, title = title, x_label = x_label, y_label = y_label)
	chart.render()
