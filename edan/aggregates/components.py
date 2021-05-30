"""
shared base container objects for macroeconomic aggregate data
"""

from __future__ import annotations

import edan.delims as dlm

from edan.containers import CompoundStorage

from edan.aggregates.disaggregate import Disaggregator


class Component(CompoundStorage):
	"""
	an economic aggregate. the key feature of these data series is they have
	(and/or are) subcomponents whose construction is based on partitions of
	the data that this aggregate is computed from
	"""

	mtypes = []

	def __init__(
		self,
		code: str,
		level: int = 0,
		long_name: str = '',
		short_name: str = '',
		source: str = '',
		table: str = '',
		**codes
	):
		# initialize CompoundStorage class with attribute names that hold data
		super().__init__(fields=self.mtypes)

		# unique edan code that identifies this Component. the edan codes
		#	corresponding to mtypes (real & nominal level, price index, etc)
		#	are assumed to be passed as keywords
		self.code = code
		for mtype in self.mtypes:
			try:
				setattr(self, f"{mtype}_code", codes[mtype])
			except KeyError:
				pass

		# attributes about relations to other Components
		self.level = level
		self.subs = []

		# display names source api
		self.long_name = long_name
		self.short_name = short_name

		# source api and economic table this component belongs to
		self.source = source
		self.table = table

	def __getitem__(self, key: str):
		if self.elemental:
			raise ValueError(f"{repr(self)} is an elemental component")

		if not isinstance(key, str):
			raise TypeError(f"'key' must be a string")

		subs = [s.code for s in self.subs]
		try:
			# assume `key` is the entire code of a subcomponent
			idx = subs.index(key)
			return self.subs[idx]

		except ValueError:
			# `key` is relative to the code of this component

			full_key = dlm.concat_codes(self.code, key)
			try:
				idx = subs.index(full_key)
				return self.subs[idx]
			except ValueError:
				raise KeyError(
					f"{repr(key)} does not match a subcomponent of {repr(self)}"
				) from None

	def disaggregate(
		self,
		subs: Union[str, Iterable[str]] = '',
		level: int = 0
	):
		"""
		locate & return a list of subcomponents that can be further down the
		subcomponent tree than just the Component objects immediately available
		in the `subs` attribute. functionality for selecting based on `edan` code
		and level relative to the current Component is provided

		Parameters
		----------
		subs : str | Iterable[str] ( = '' )
			an iterable of subcomponents, or single subcomponent, to return. the
			elements of `subs` are assumed to be (relative or absolute) `edan` codes
		level : int ( = 0 )
			the level, relative to the current Component, of subcomponents that
			are to be returned. if a subcomponent has level `l`, with
			l < level + self.level, and that subcomponent is elemental, it is also
			included

		Returns
		-------
		disaggregate : Disaggregator iterable
		"""

		if self.elemental:
			raise TypeError(f"{repr(self)} is elemental & cannot be disaggregated")

		return Disaggregator(self, subs, level)

	def is_less(self, rel=''):
		"""
		boolean for if this component should be subtracted from super-component
		when summing nominal levels or computing contributions
		"""
		if rel:
			if '~' not in self.code:
				return False
			if dlm.contains(rel, self.code):
				return '~' not in rel
			else:
				return False
		else:
			code = dlm.EdanCode(self.code)
			try:
				last_delim = code.delims[-1]
				if last_delim == '~':
					return True
				return False
			except IndexError:
				return False

	def __repr__(self):
		klass = self.__class__.__name__
		return f"{klass}({self.code}, {self.level})"

	@property
	def elemental(self):
		"""return True if there are no subcomponents"""
		if self.subs:
			return False
		return True

	@classmethod
	def from_registry(cls, dct: dict):
		mtypes = {g: dct.get(g) for g in cls.mtypes if dct.get(g)}
		return cls(
			dct['code'],
			dct['__level__'],
			dct['long_name'],
			dct['short_name'],
			dct['source'],
			dct['__table__'],
			**mtypes
		)


class FlowComponent(Component):
	"""
	a macroeconomic component that represents a flow variable, as opposed
	to the normal stock ones. for example, changes to PDI
	"""
	pass

class BalanceComponent(Component):
	"""
	a macroeconomic component that represents an intratemporal difference of two
	stock components. for example, net exports and gross output of nonprofit
	institutions
	"""
	pass
