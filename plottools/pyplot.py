
import matplotlib.pyplot as plt
from ._plotengine import Engine

class PyplotXY(Engine):
	@staticmethod
	def _setkeyParameters(kwargs):
		"""
			Keyword Arguements
			------------------
				figsize: tuple<int, int>
		"""
		if 'style' in kwargs:
			plt.style.use(kwargs['style'])

	def _createInitialPlot(self, kwargs):
		# Holds keyword arguments for every series.
		self.data = dict()

		# The basic plots
		self.figure, self.chart = plt.subplots(figsize = kwargs['figsize'])

	def _getDefaultKeywordArguments(self, kwargs):
		kwargs['figsize'] = kwargs.get('figsize', (20, 10))
		kwargs['style'] = kwargs.get('style', 'fivethirtyeight')
		return kwargs

	def addLabels(self, **kwargs):
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

	def addSeries(self, series = None, **kwargs):
		""" Adds a set of x and y value pairs to the plot.
			Parameters
			----------
				series: list of x-y value pairs.
					'x' and 'y' keyword arguments may be used instead.
			Keyword Arguments
			-----------------
				'x', 'y': list<number> [Required if 'series' is None and 'y' is given]
					x-values to pair with the additional 'y' keyword.
				color: string
					The desired color for the series.
				label: string
					name of the series. if absent, a name will automatically be generated.
		"""
		if series is None:
			x = kwargs['x']
			y = kwargs['y']
		else:
			x, y = zip(*series)

		label = kwargs.get('label', self._generateSeriesLabel())
		color = kwargs.get('color', self._generateSeriesColor())

		self.chart.scatter(x = x, y = y, c = color, label = label)

	@staticmethod
	def render(filename = None):
		""" Renders the plot """
		if filename is None:
			plt.show()