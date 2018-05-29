"""
	A version of timetools built on Pendulum. Pendulum has a number of great features, but suffers from the
	same drawbacks as other Date/time modules when creating an object from another object or uncommon format.
	Pendulum also does not offer convienience methods for some datetime representations (ex. ISO durations).
	Ex. pandas.Timestamp is not compatible with pendulum.datetime.
"""

import pendulum
from typing import Any

class Duration(pendulum.Duration):
	@classmethod
	def from_object(cls, obj:Any):
		pass
	def to_iso(self):
		pass
