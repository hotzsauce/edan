"""
module for CPI components
"""

from edan.accessors import CachedAccessor

from edan.aggregates.series import Series
from edan.aggregates.components import Component
from edan.aggregates.modifications import ModificationAccessor

from edan.plotting.cpi import CPIPlotAccessor



class CPISeries(Series):

	def __init__(
		self,
		code: str, mtype: str, obj: Component,
		*args, **kwargs
	):
		super().__init__(code, source=obj.source)

		self.mtype = mtype
		self.obj = obj

	# add accessor for functions of data
	modify = CachedAccessor('modify', ModificationAccessor)

class CPIComponent(Component):

	mtypes = ['price']

	@property
	def price(self):
		"""
		access the CPISeries corresponding to the price index of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the CPISeries were changed
		"""
		if hasattr(self, '_price'):
			return self._price
		else:
			self._price = CPISeries(self.price_code, 'price', self)
			return self._price

	# add accessor for plotting
	plot = CachedAccessor('plot', CPIPlotAccessor)
