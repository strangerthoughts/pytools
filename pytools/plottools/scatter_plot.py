import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from typing import List, Dict, Optional, Union, SupportsFloat, SupportsInt, Tuple
from pytools import numbertools
from dataclasses import dataclass
from pathlib import Path

NumberType = Union[SupportsFloat, SupportsInt]
SeriesType = List[Tuple[NumberType, NumberType]]

plt.style.use('fivethirtyeight')

@dataclass
class ScatterPlotOptions:
	# Hold options relevant to the scatter plot. Implemented to make the usable options clearer.
	figsize:Tuple[int,int] = (20, 10)
	style: str = 'fivethirtyeight'


class ScatterPlot:
	def __init__(self, data: Optional[SeriesType] = None, **kwargs):
		self._series_variables = dict()
		self.options = self._get_default_keyword_arguments(kwargs)
		self.options = kwargs
		self._create_initial_plot()

		self.add_labels(**kwargs)

		self.add_series(data, **kwargs)

	def _create_initial_plot(self) -> None:
		# Holds keyword arguments for every series.
		self.data = dict()

		def formatter(x, pos):
			return numbertools.human_readable(x, precision = 1)

		# The basic plots
		self.figure, self.ax = plt.subplots(figsize = self.options['figsize'])
		self.ax.yaxis.set_major_formatter(tkr.FuncFormatter(formatter))

	@staticmethod
	def _get_default_keyword_arguments(kwargs: Dict) -> ScatterPlotOptions:
		options = ScatterPlotOptions(
			figsize = kwargs.get('figsize', (20, 10)),
			style = kwargs.get('style', 'fivethirtyeight')
		)
		return options

	def add_labels(self, title:str=None, xlabel:str=None,ylabel:str=None) -> None:
		""" labels various parts of the map.
			Parameters
			-----------------
			title: string
				The title of the plot
			xlabel: string
			ylabel: string
		"""

		if title:
			self.figure.suptitle(title)
		if xlabel:
			plt.xlabel(xlabel)
		if ylabel:
			plt.ylabel(ylabel)

	def add_legend(self, kwargs):
		pass

	def add_series(self, x: SeriesType, y: Optional[SeriesType] = None, **kwargs)->None:
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

		label = kwargs.get('label', self._generate_series_label())
		color = kwargs.get('color', self._generate_series_color())

		self.ax.scatter(x = x, y = y, c = color, label = label)

	@staticmethod
	def render(filename: Union[str,Path] = None)->None:
		""" Renders the plot """
		if filename is None:
			plt.show()

	@staticmethod
	def _generate_series_color() -> str:
		color = "#AA5588"
		return color

	def _generate_series_label(self) -> str:
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

	chart = ScatterPlot(data, title = title, x_label = x_label, y_label = y_label)
	chart.render()
