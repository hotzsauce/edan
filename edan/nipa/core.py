"""
module for NIPA components
"""

from __future__ import annotations

from edan.accessors import CachedAccessor

from edan.aggregates.series import Series
from edan.aggregates.components import Component

from edan.nipa.features import Contribution
from edan.nipa.modifications import ModificationAccessor

from edan.plotting.nipa import NIPAPlotAccessor


class NIPASeries(Series):

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


class NIPAComponent(Component):

	mtypes = ['quantity', 'price', 'nominal', 'real']

	@property
	def quantity(self):
		"""
		access the NIPASeries corresponding to the quantity index of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the NIPASeries were changed
		"""
		if hasattr(self, '_quantity'):
			return self._quantity
		else:
			self._quantity = NIPASeries(self.quantity_code, 'quantity', self)
			return self._quantity

	@property
	def price(self):
		"""
		access the NIPASeries corresponding to the price index of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the NIPASeries were changed
		"""
		if hasattr(self, '_price'):
			return self._price
		else:
			self._price = NIPASeries(self.price_code, 'price', self)
			return self._price

	@property
	def nominal(self):
		"""
		access the NIPASeries corresponding to the nominal level of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the NIPASeries were changed
		"""
		if hasattr(self, '_nominal'):
			return self._nominal
		else:
			self._nominal = NIPASeries(self.nominal_code, 'nominal', self)
			return self._nominal

	@property
	def real(self):
		"""
		access the NIPASeries corresponding to the real level of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the NIPASeries were changed
		"""
		if hasattr(self, '_real'):
			return self._real
		else:
			self._real = NIPASeries(self.real_code, 'real', self)
			return self._real

	# add accessor for plotting
	plot = CachedAccessor('plot', NIPAPlotAccessor)

	# add accessors for common features
	contribution = CachedAccessor('contribution', Contribution)
