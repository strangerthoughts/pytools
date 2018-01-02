
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