class ArraySizeError(Exception):
    """ Exception to raise if the specified rows do not match the number of columns in the table.
	"""

    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message, '')

    def __str__(self):
        return self.message

class DisplayTable:
	def __init__(self, max_width = 120, columns = None, **kwargs):
		"""
			Parameters
			----------
			max_width: int; default 120
				Maximum width for each column. 0 indicates unlimited width
			columns: list<str>; default None
				The table's header. 
			
			Keyword Arguments
			-----------------
		"""

		self.max_width = max_width if max_width >= 0 else 120
		self._vchar, self._hchar, self.corner, self.header = self.setDeco(False)

		if not self.columns:
			self.reset()
		else:
			self._rows = kwargs.get('rows', kwargs.get('data', list()))
			self._row_size = len(self.columns)

	def validate_row(self, array):
		_validation = self._row_size and len(array) == self._row_size 
		if not _validation:
			raise ArraySizeError


	def reset(self):
		self.columns = list()
		self.rows = list()
		self._row_size = None
	
	def setAlignment(self, array):
		""" Sets the alignement of each row.
			Parameters
			----------
			array: list<'l' | 'c' | 'r'|>
				'l': left
				'c': center
				'r': right
		"""

	def setDeco(self, _set_vals = True, **kwargs):
		""" Sets the characters to use as table/row/column/header borders.
			Keyword Arguments
			-----------------
			'horizontal': str; default '-'
				The characters used to separate each line
			'vertical': str; default '|'
				The character to separate each column. 
			'corner': str; default '+'
				The charater representing a column/row corner
			'header': str; default '='
				The character separating the column names from the column values. 
			'scheme': str; default 'basic'
				Sets a pre-defined scheme.
		"""

		_scheme = kwargs.get('scheme')
		if not _scheme:
			_hchar = kwargs.get('horizontal', '-')
			_vchar = kwargs.get('vertical', '|')
			_corner = kwargs.get('corner', '+')
			_header = kwargs.get('header', '=')
		elif _scheme == 'basic':
			_hchar, _vchar, _corner, _header = self.setDeco() 
		else:
			raise NotImplementedError
		if _set_vals:
			self._hchar = _hchar
			self._vchar = _vchar
			self._corner = _corner
			self._header = _header
		else:
			#Used when creating the table
			return _hchar, _vchar, _corner, _header
	
	def setFormat(self, array):
		""" Sets the format for each row. Requires a format for each column.
			Formats
			-------
				'a': automatically format based on the cell value
				'i': formt as an integer
				'f': format as a float
				'e': format as an exponential float
				'%': format as a percentage
				't': format as regular text
				callable: a method tht takes the value as an argument and returns a string.
		"""
	

