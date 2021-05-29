"""
module for NIPA components
"""

from __future__ import annotations

from edan.delims import EdanCode
from edan.accessors import CachedAccessor

from edan.aggregates.series import Series
from edan.aggregates.components import (
	Component,
	FlowComponent,
	BalanceComponent
)
from edan.aggregates.modifications import ModificationAccessor

from edan.nipa.features import Contribution

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
	def is_less(self):
		"""
		boolean for if this component should be subtracted from super-component
		when summing nominal levels or computing contributions
		"""
		code = EdanCode(self.code)
		try:
			last_delim = code.delims[-1]
			if last_delim == '-':
				return True
			return False
		except IndexError:
			return False

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


class NIPAFlowComponent(NIPAComponent, FlowComponent):

	mtypes = ['nominal', 'real']


class NIPABalanceComponent(NIPAComponent, BalanceComponent):

	mtypes = ['quantity', 'price', 'nominal', 'real']


def component_type(ctype: str):
	"""
	used in edan/nipa/api.py when constructing the PCE and GDP tables
	"""
	if ctype == 'stock':
		return NIPAComponent
	elif ctype == 'flow':
		return NIPAFlowComponent
	elif ctype == 'balance':
		return NIPABalanceComponent

	raise ValueError(ctype)
