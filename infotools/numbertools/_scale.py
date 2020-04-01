import math
from dataclasses import dataclass, field
from typing import List, Optional, SupportsAbs

from fuzzywuzzy import process


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


class Scale:
	def __init__(self):
		self.decimal_base = 10
		self.binary_base = 1024

		self.decimal_system = self._load_decimal_system()
		self.binary_system = self._load_binary_system()

	def _get_unit_magnitude(self, system) -> Magnitude:
		system = self._select_system(system)
		if system == 'decimal':
			return system[6]
		else:
			# Invalid systems should be handled by self._select_system.
			return system[0]

	def _load_decimal_system(self) -> List[Magnitude]:
		system = [
			Magnitude('atto', 'a', self.decimal_base ** -18),
			Magnitude('femto', 'f', self.decimal_base ** -15),
			Magnitude('pico', 'p', self.decimal_base ** -12),
			Magnitude('nano', 'n', self.decimal_base ** -9),
			Magnitude('micro', 'u', self.decimal_base ** -6, ["μ", 'millionths']),
			Magnitude('milli', 'm', self.decimal_base ** -3, ['thousandths']),
			Magnitude('', '', 1, ['unit', 'one']),
			Magnitude('kilo', 'K', self.decimal_base ** 3, ['thousand']),
			Magnitude('mega', 'M', self.decimal_base ** 6, ['million']),
			Magnitude('giga', 'B', self.decimal_base ** 9, ['billion']),
			Magnitude('tera', 'T', self.decimal_base ** 12, ['trillion']),
			Magnitude('peta', 'P', self.decimal_base ** 15, ['quadrillion']),
			Magnitude('exa', 'E', self.decimal_base ** 18, ['quintillion'])
		]

		return system

	def _load_binary_system(self) -> List[Magnitude]:
		system = [
			Magnitude('', '', self.binary_base ** 0, ['unit', '']),
			Magnitude('kibi', 'K', self.binary_base ** 1, ['thousand']),
			Magnitude('mebi', 'M', self.binary_base ** 2, ['million']),
			Magnitude('gibi', 'B', self.binary_base ** 2, ['billion']),
			Magnitude('tebi', 'T', self.binary_base ** 4, ['trillion']),
			Magnitude('pebi', 'P', self.binary_base ** 5, ['quadrillion']),
			Magnitude('exbi', 'E', self.binary_base ** 6, ['quintillion']),
			Magnitude('zebi', 'Z', self.binary_base ** 7, []),
			Magnitude('yobi', 'Y', self.binary_base ** 8, [])
		]

		return system

	def _select_system(self, system: str) -> List[Magnitude]:
		if system == 'decimal':
			return self.decimal_system
		elif system == 'binary':
			return self.binary_system
		else:
			message = f"'{system}' is not a valid system."
			raise ValueError(message)

	@staticmethod
	def is_null(value) -> bool:
		""" Checks if a value represents a null value."""
		try:
			result = value is None or math.isnan(float(value))
		except (TypeError, ValueError):
			result = True

		return result

	def get_magnitude_from_value(self, value: SupportsAbs, system = 'decimal') -> Magnitude:
		value = abs(value)
		system = self._select_system(system)

		if value == 0.0 or self.is_null(value):
			return self._get_unit_magnitude(system)

		for _scale in system[::-1]:
			if value >= _scale.multiplier:
				magnitude = _scale
				break
		else:
			message = f"'{value}' does not have a defined base."
			raise ValueError(message)

		return magnitude

	def get_magnitude_from_prefix(self, prefix: str, system: str = "decimal") -> Optional[Magnitude]:
		system = self._select_system(system)
		try:
			candidates = [i for i in system if i.prefix == prefix]
			return candidates[0]
		except IndexError:
			return None

	def get_magnitude_from_alias(self, alias: str) -> Optional[Magnitude]:
		for element in self.decimal_system + self.binary_system:
			if not element.alias:
				# Don't bother with empty aliases.
				continue
			candidate, score = process.extractOne(alias.lower(), element.alias)
			if score > 90:
				return element
		# Added to make it clear the method should return `None`
		return None


scale = Scale()

if __name__ == "__main__":
	pass
