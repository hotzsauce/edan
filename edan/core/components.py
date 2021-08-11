"""
shared base container objects for macroeconomic aggregate data
"""

from __future__ import annotations

import edan.delims as dlm

from edan.errors import MeasureTypeError

from edan.core.base import BaseComponent

from edan.core.series import Series
from edan.core.disaggregate import Disaggregator

from edan.accessors import CachedAccessor
from edan.plotting.core import ComponentPlotAccessor


class Component(BaseComponent):
	"""
	an economic aggregate. the key feature of these data series is they have
	(and/or are) subcomponents whose construction is based on partitions of
	the data that this aggregate is computed from
	"""

	mtypes = []
	_series_obj = Series
	_default_mtype = ''

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

	def __getattr__(self, attr):
		"""
		created to address Issue #9. this basically gets around needing to have
		large blocks of code in every subclass of Component dedicated to just
		returning the Series corresponding to the requested mtype. python calls
		the `__getattr__` method after `__getattribute__`, which checks to see if
		the parameter is an attribute of the class, and if it is, returns immediately.
		if it's not, `__getattr__` will be called.
		"""
		if attr in self.mtypes:
			code = f"{attr}_code"

			try:
				series_code = self.__getattribute__(code)
				hidden_series_name = f"_{attr}"

				try:
					return self.__getattribute__(hidden_series_name)
				except AttributeError:
					series_code = self.__getattribute__(code)
					series = self._series_obj(
						code=series_code,
						mtype=attr,
						comp=self
					)

					setattr(self, hidden_series_name, series)
					return series

			except AttributeError:
				raise MeasureTypeError(measure=attr, comp=self)

		raise AttributeError(f"Component class does not have {attr} attribute")


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
	def default_mtype(self):
		"""return the Series object representing the default mtype"""
		if self._default_mtype:
			return self.__getattr__(self._default_mtype)
		raise TypeError(f"{repr(self)} has no default mtype")

	@property
	def elemental(self):
		"""return True if there are no subcomponents"""
		if self.subs:
			return False
		return True

	@property
	def display_name(self):
		"""name to use in any plots with this component"""
		if self.short_name:
			return self.short_name
		return self.long_name

	@classmethod
	def from_registry(cls, dct: dict):
		mtypes = {g: dct.get(g) for g in cls.mtypes if dct.get(g)}
		return cls(
			code=dct['code'],
			level=dct['__level__'],
			long_name=dct['long_name'],
			short_name=dct['short_name'],
			source=dct['source'],
			table=dct['__table__'],
			**mtypes
		)

	# add accessor for plotting
	plot = CachedAccessor('plot', ComponentPlotAccessor)


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
