"""
module for NIPA components
"""

from __future__ import annotations

import re

from edan.accessors import CachedAccessor
from edan.containers import (
	CoreSeries,
	CompoundStorage
)

from edan.data.retrieve import retriever

from edan.nipa.features import Contribution
from edan.nipa.modifications import ModificationAccessor

from edan.plotting.nipa import NIPAPlotAccessor


class NIPASeries(CoreSeries):

	def __init__(
		self,
		code: str, dtype: str, obj: Component,
		*args, **kwargs
	):
		if code:
			data, meta = retriever.retrieve(code, source=obj.source)
			super().__init__(code, data)

			self.meta = meta
		else:
			super().__init__(code)
			self.meta = None

		self.dtype = dtype
		self.obj = obj


	def __repr__(self):
		return f"NIPASeries({self.code})"

	# add accessor for functions of data
	modify = CachedAccessor('modify', ModificationAccessor)


class Component(CompoundStorage):
	"""
	a collection of NIPASeries that represents a single Component
	"""

	edan_delimiters = (':', '+', '-')

	def __init__(
		self,
		code: str,
		qcode: str = '',
		pcode: str = '',
		ncode: str = '',
		rcode: str = '',
		level: int = 0,
		long_name: str = '',
		short_name: str = '',
		source: str = ''
	):
		# initialize CompoundStorage class with attribute names that hold data
		super().__init__(fields=('quantity', 'price', 'nominal', 'real'))

		# various codes for referencing the different data comprising this Component
		self.code = code
		self.qcode = qcode
		self.pcode = pcode
		self.ncode = ncode
		self.rcode = rcode

		# attributes about relations to other Components
		self.level = level
		self.subs = []
		self.sups = ''

		# display names & source api
		self.long_name = long_name
		self.short_name = short_name
		self.source = source



	def __getitem__(self, key: str):
		if self.elemental:
			raise TypeError(f"{repr(self)} is an elemental component")

		subs = [s.code for s in self.subs]
		try:
			# assume `key` is the entire code of a subcomponent
			idx = subs.index(key)
			return self.subs[idx]

		except ValueError:
			# `key` is a partial code of the subcomponent

			regex_pattern = '|'.join(map(re.escape, self.edan_delimiters))
			split_code = re.split(regex_pattern, self.code)
			split_key = re.split(regex_pattern, key)

			overlap = len(split_key) - 1
			full_key = ':'.join(split_code[:overlap]) + ':' + key

			idx = subs.index(full_key)
			return self.subs[idx]

	@property
	def elemental(self):
		"""return True if there are no subcomponents"""
		if self.subs:
			return False
		return True

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
			self._quantity = NIPASeries(self.qcode, 'quantity', self)
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
			self._price = NIPASeries(self.pcode, 'price', self)
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
			self._nominal = NIPASeries(self.ncode, 'nominal', self)
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
			self._real = NIPASeries(self.rcode, 'real', self)
			return self._real

	@classmethod
	def from_registry(self, dct: dict):
		return Component(
			dct['code'],
			dct['quantity'],
			dct['price'],
			dct['nominal'],
			dct['real'],
			dct['level'],
			dct['long_name'],
			dct['short_name'],
			dct['source']
		)

	def __repr__(self):
		return f"Component({self.code}, {self.level})"

	# add accessor for plotting
	plot = CachedAccessor('plot', NIPAPlotAccessor)

	# add accessors for common features
	contribution = CachedAccessor('contribution', Contribution)
