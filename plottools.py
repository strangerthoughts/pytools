import pygal

import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')


class Engine:
	""" Base class to implement a generalized fromawork for using difference plotting libraries.
	"""
	def __init__(self, engine = 'pyplot', **kwargs):
		self.engine = engine
		self._series_variables = dict()
		kwargs = self._getDefaultKeywordArguments(kwargs)
		self.kwargs = kwargs
		self._setKeyParameters(kwargs)
		self._createInitialPlot(kwargs)
		self._setupPlot(kwargs)

		self.addLabels(**kwargs)
		if 'series' in kwargs or 'x' in kwargs:
			self.addSeries(**kwargs)

	def _createInitialPlot(self, kwargs):
		pass

	def _getDefaultKeywordArguments(self, kwargs):
		return kwargs

	@staticmethod
	def _generateSeriesColor():
		color = "#AA5588"
		return color

	def _generateSeriesLabel(self):
		""" Automatically generates a label for a series based on the number
			of previously generated plots.
		"""

		_series_index = len(self._series_variables.keys()) + 1
		label = "series{0}".format(_series_index)
		return label
	
	def _setupPlot(self, kwargs):
		pass

	def _setKeyParameters(self, kwargs):
		pass

	def addLabels(self, **kwargs):
		message = "Engine.addLabels is not implemented."
		raise NotImplementedError(message)

	def addLegend(self, **kwargs):
		pass

	def addSeries(self, **kwargs):
		message = "Engine.addSeries is not implemented."
		raise NotImplementedError(message)

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


class PygalXY(Engine):
	def _createInitialPlot(self, kwargs):
		self.chart = pygal.XY()

	def addLabels(self, **kwargs):
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
			x = kwargs.get('x')
			y = kwargs.get('y')
			series = list(zip(x, y))
		
		label = self._generateSeriesLabel()
		# color = self._generateSeriesColor(**kwargs)
		
		self.chart.add(label, series)

	def render(self, filename = None):
		""" Renders the plot.
			Parameters
			----------
				filename: string
					Path to render an svg file to.
		"""
		if filename is None:
			self.chart.render()
		else:
			self.chart.render_to_file(filename)


def debug():
	import math
	label = 'Test Plot'
	xlabel = 'The x axis'
	ylabel = 'The y axis'
	series_a = [(x / 10., math.cos(x / 10.)) for x in range(-50, 50, 5)]

	test = PygalXY(series = series_a, title = label, xlabel = xlabel, ylabel = ylabel)
	test.render('test_plot.svg')

if __name__ == "__main__":
	debug()
