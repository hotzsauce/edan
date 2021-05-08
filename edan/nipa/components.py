"""
module for gdp components
"""

from __future__ import annotations

from edan.accessors import CachedAccessor
from edan.containers import (
	CoreSeries,
	CompoundStorage
)

from edan.nipa.base import ABCComponent

from edan.nipa.features import (
	Nominal,
	Contribution
)

from edan.nipa.modifications import ModificationAccessor

from edan.plotting.gdp import GDPPlotAccessor


class GDPSeries(CoreSeries):

	def __init__(
		self,
		name: str, code: str, gtype: str, obj: Component,
		*args, **kwargs
	):
		# data = get_series(code) if code else None
		# super().__init__(name, data)

		# self.meta = get_metadata(code)
		self.code = code
		self.gtype = gtype
		self.obj = obj


	def __repr__(self):
		return f"GDPSeries({self.name})"

	# add accessor for functions of data
	modify = CachedAccessor('modify', ModificationAccessor)


class Component(CompoundStorage, ABCComponent):
	"""
	a collection of GDPSeries, usually just a real level series & a price index
	series that represents a single GDP component.

	Attributes
	----------
	name : str
		the human-readable name of the GDP component; e.g. 'bfi' or 'serv'
	"""


	def __init__(self, name: str,
		level_code: str = '', price_code: str = '',
		subs: list = [], sups: list = [],
		long_name: str = '', short_name: str = ''
	):
		# initialize CompoundStorage class with attribute names that hold data
		super().__init__(fields=('level', 'price'))

		self.name = name
		self.level_code = level_code
		self.price_code = price_code

		# sub- and super-components. when initialized via .from_json, these are
		#	component names, but later converted to Components in edan.gdp.api
		self._subs = subs
		self._sups = sups

		self.long_name = long_name
		self.short_name = short_name

		# attributes for GDPSeries
		self._level, self._price = None, None


	@property
	def level(self):
		"""
		access the GDPSeries corresponding to the real level of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the GDPSeries were changed
		"""
		if self._level:
			return self._level
		else:
			name = f"{self.name}_level"
			self._level = GDPSeries(name, self.level_code, 'level', self)
			return self._level


	@property
	def price(self):
		"""
		access the GDPSeries corresponding to the price index of this Component.
		It's implemented this way, and not with @cached_property, because I don't
		think the decorator could tell if attributes of the GDPSeries were changed
		"""
		if self._price:
			return self._price
		else:
			name = f"{self.name}_price"
			self._price = GDPSeries(name, self.price_code, 'price', self)
			return self._price


	@property
	def subs(self):
		return self.subcomponents

	@property
	def subcomponents(self):
		return self._subs


	def __getitem__(self, key):
		"""indexing into Component returns a subcomponent by name"""
		names = [sc.name for sc in self._subs]
		try:
			idx = names.index(key)
			return self._subs[idx]
		except ValueError:
			raise KeyError(f"'{key}' is not a subcomponent of {self.short_name}")


	@classmethod
	def from_json(cls, d):
		"""
		classmethod for constructing a Component instance from the existing
		json registry
		"""
		return Component(
			d['name'], d['level'], d['price'], d['subs'], d['sups'],
			d['long_name'], d['short_name']
		)


	def __repr__(self):
		return f"Component[{self.name}]"


	# add accessor for plotting
	plot = CachedAccessor('plot', GDPPlotAccessor)

	# add accessors for common features
	nominal = CachedAccessor('nominal', Nominal)
	contribution = CachedAccessor('contribution', Contribution)
