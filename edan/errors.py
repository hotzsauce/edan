"""
module for errors encountered when interacting with heierarchical data
"""
from __future__ import annotations


class EdanError(Exception):
	"""base class for errors in edan processes"""

class MeasureTypeError(EdanError, TypeError):
	"""
	raised in two cases:
		(1) when a Component doesn't have a particular measure
		(2) when a process is being applied to a Series of a mtype for which
			that process makes no economic sense

	an example of the first case:  net exports doesn't have price or quantity
	indices so either of the following would raise a MeasureTypeError:

		>>> nx = edan.nipa.GDPTable['gdp:nx']
		>>> nx.price	# error
		>>> nx.quantity # error
	"""
	def __init__(self, measure: str, comp: Component = None):
		if comp:
			msg = f"{repr(comp)} does not have mtype {repr(measure)}"
			super().__init__(msg)
		else:
			super().__init__(repr(measure))

