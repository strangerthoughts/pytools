import math
from dataclasses import dataclass, field
from typing import *

from fuzzywuzzy import process

NumberType = Union[int, float]


@dataclass
class Magnitude:
	""" Provides an easy method of checking the magnitude of numbers."""
	prefix: str
	suffix: str
	multiplier: float
	alias: List[str] = field(default_factory = list)  # Alternative methods of referring to this multiplier.

	@staticmethod
	def _get_other(other):
		""" Returns the value in `other` that the dunder methods need to compare.
		"""
		if hasattr(other, 'multiplier'):
			return other.multiplier
		else:
			return other

	def __float__(self) -> float:
		return float(self.multiplier)

	def __post_init__(self):
		self.alias.append(self.prefix)

	def __mul__(self, other) -> float:
		return self._get_other(other) * self.multiplier

	def __rmul__(self, other) -> float:
		return self.__mul__(other)

	def __ge__(self, other):
		other = self._get_other(other)
		return self.multiplier >= other

	def __gt__(self, other) -> bool:
		other = self._get_other(other)
		return self.multiplier > other

	def __lt__(self, other):
		other = self._get_other(other)
		return self.multiplier < other

	def __le__(self, other):
		other = self._get_other(other)
		return self.multiplier <= other

	def __eq__(self, other):
		other = self._get_other(other)
		return self.multiplier == other

	def is_match(self, value: str) -> bool:
		""" Returns True if the passed string corresponds to this scale."""
		selected_scale = False
		if self.prefix == value or self.suffix == value:
			selected_scale = True
		else:
			scale_alias, score = process.extractOne(value.lower(), self.alias)
			if score > 90:
				selected_scale = True
		return selected_scale


class AbstractScale:

	@staticmethod
	def is_null(value) -> bool:
		""" Checks if a value represents a null value."""
		try:
			result = value is None or math.isnan(float(value))
		except (TypeError, ValueError):
			result = True

		return result

	def get_unit_magnitude(self):
		raise NotImplementedError

	def get_magnitude_from_value(self, value: SupportsAbs) -> Magnitude:
		value = abs(value)

		if value == 0.0 or self.is_null(value):
			return self.get_unit_magnitude()

		for _scale in self.system[::-1]:
			if value >= _scale.multiplier:
				magnitude = _scale
				break
		else:
			message = f"'{value}' does not have a defined base."
			raise ValueError(message)

		return magnitude

	def get_magnitude_from_prefix(self, prefix: str) -> Optional[Magnitude]:
		try:
			candidates = [i for i in self.system if i.prefix == prefix]
			return candidates[0]
		except IndexError:
			return None

	def get_magnitude_from_alias(self, alias: str) -> Optional[Magnitude]:
		for element in self.system:
			if not element.alias:
				# Don't bother with empty aliases.
				continue
			candidate, score = process.extractOne(alias.lower(), element.alias)
			if score > 90:
				return element
		# Added to make it clear the method should return `None`
		return None



class DecimalScale(AbstractScale):
	def __init__(self):
		self.base = 10
		self.system = [
			Magnitude('atto', 'a', self.base ** -18),
			Magnitude('femto', 'f', self.base ** -15),
			Magnitude('pico', 'p', self.base ** -12),
			Magnitude('nano', 'n', self.base ** -9),
			Magnitude('micro', 'u', self.base ** -6, ["μ", 'millionths']),
			Magnitude('milli', 'm', self.base ** -3, ['thousandths']),
			Magnitude('', '', 1, ['unit', 'one']),
			Magnitude('kilo', 'K', self.base ** 3, ['thousand']),
			Magnitude('mega', 'M', self.base ** 6, ['million']),
			Magnitude('giga', 'B', self.base ** 9, ['billion']),
			Magnitude('tera', 'T', self.base ** 12, ['trillion']),
			Magnitude('peta', 'P', self.base ** 15, ['quadrillion']),
			Magnitude('exa', 'E', self.base ** 18, ['quintillion'])
		]

	def get_unit_magnitude(self) -> Magnitude:
		return self.system[6]


class BinaryScale(AbstractScale):
	def __init__(self):
		self.base = 1024
		self.system = [
			Magnitude('', '', self.base ** 0, ['unit', '']),
			Magnitude('kibi', 'K', self.base ** 1, ['thousand']),
			Magnitude('mebi', 'M', self.base ** 2, ['million']),
			Magnitude('gibi', 'B', self.base ** 2, ['billion']),
			Magnitude('tebi', 'T', self.base ** 4, ['trillion']),
			Magnitude('pebi', 'P', self.base ** 5, ['quadrillion']),
			Magnitude('exbi', 'E', self.base ** 6, ['quintillion']),
			Magnitude('zebi', 'Z', self.base ** 7, []),
			Magnitude('yobi', 'Y', self.base ** 8, [])
		]

	def get_unit_magnitude(self):
		return self.system[0]


if __name__ == "__main__":
	pass
