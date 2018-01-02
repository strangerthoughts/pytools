import pygal
from ._plotengine import Engine


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
