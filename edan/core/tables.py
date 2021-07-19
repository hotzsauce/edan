"""
module for tables of aggregated data. the Table object functions as a
mapping from series codes (the `edan` codes) to the Components themselves
"""

from __future__ import annotations

import os
import functools
from copy import deepcopy

from edan.utils.dtypes import iterable_not_string


class TableIterator(object):
	"""
	iterator constructor for the Table class. we split the iterator and the
	data container following mgilson's comment in the thread
	https://stackoverflow.com/questions/21665485/how-to-make-a-custom-object-iterable
	which in turn is apparently based on what Python does under the hood

	iterating over a Table returns the names of the series in it
	"""

	def __init__(self, names: Iterable):
		self.idx = 0
		self.data = names

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self.data[self.idx-1]
		except IndexError:
			self.idx = 0
			raise StopIteration


class TablePrettyPrinter(object):
	"""
	pretty print the contents of a Table to the console
	"""
	vert = '|'
	horz = '-'
	dhorz = '='
	lwidth = 2
	rwidth = 2
	ellipses = ' ...'

	def __init__(self, table):
		self.category = table.category
		self.info = [(c.level, c.long_name) for c in table.rows.values()]

	def get_console_config(self):
		size = os.get_terminal_size()
		return size.columns, size.lines

	def print(self):
		cols, lines = self.get_console_config()

		entry_gap = ' '*self.lwidth # gap in each row before any branch
		branch = ' '*self.lwidth + self.vert + ' '*(self.rwidth-1)
		leaf = ' '*self.lwidth + self.vert + self.horz*self.rwidth
		pad = len(self.ellipses)

		table = self.category + ' Table\n'
		for level, name in self.info:
			if level:
				prefix = branch*(level - 1) + leaf
			else:
				# if this is a top-level component, add a long row of double lines
				table = table + entry_gap + self.dhorz*(cols-self.lwidth) + '\n'
				prefix = ''

			row_str = entry_gap + prefix + name
			if len(row_str) - pad > cols:
				row_str = row_str[:(cols-pad)] + self.ellipses

			table = table + row_str + '\n'

		return table


class Table(object):
	"""
	representation of a table of economic data where each row is a variable that
	is either composed of subcomponents (that lie visually below it in the table),
	or is an 'elemental' series that has no subcomponents. access the Component
	object for each variable by indexing into the table:

		>>> tb = Table([list of PCE Component objects], 'PCE')
		>>> tb['pce']
		Component('pce', 0)

	iterating over the table is similar to iterating over a dictionary of the
	form 'name': Component; doing so yields an iterator of the component names:

		>>> for comp in tb:
		>>>		print(comp)
		'pce'
		'pce:g'
		'pce:g:d'
		...
	"""

	def __init__(
		self,
		aggregates: list,
		category: str = ''
	):
		# the top-level series in the table, and a table name
		self.aggregates = aggregates
		self.category = category

		# every series in the table as a mapping of {series_code: Component}
		self.rows = {}
		def add_series(comp):
			self.rows[comp.code] = comp
			for sub in comp.subs:
				add_series(sub)

		for agg in self.aggregates:
			add_series(agg)

	def __getitem__(self, key: Union[str, int, Iterable[str, int]]):
		if iterable_not_string(key):
			comps = []
			for k in key:
				if isinstance(k, str):
					comps.append(self.rows[k])
				elif isinstance(k, int):
					comps.append(self.rows[self._codes[k]])
				else:
					self._error(k)

			return tuple(comps)

		elif isinstance(key, str):
			try:
				return self.rows[key]
			except:
				self._error(key)

		elif isinstance(key, int):
			try:
				return self.rows[self._codes[key]]
			except:
				self._error(key)

		elif isinstance(key, slice):

			def _get_idx(k):
				try:
					return self._codes.index(k)
				except ValueError:
					self._error(k)

			start, stop = key.start, key.stop
			start = _get_idx(start) if isinstance(start, str) else start
			stop = _get_idx(stop) if isinstance(stop, str) else stop

			comps = []
			for k in range(start, stop):
				try:
					code = self._codes[k]
				except IndexError:
					raise self._error(k)
				comps.append(self.rows[code])

			return tuple(comps)

		else:
			raise TypeError(
				f"{type(key)}. table keys can be str, int, slice,  or an iterable "
				"of those str and int"
			) from None

	def __iter__(self):
		return TableIterator(self._codes)

	def __repr__(self):
		return f"{self.category} Table"

	def __str__(self):
		printer = TablePrettyPrinter(self)
		return printer.print()

	def __len__(self):
		return len(self.rows)

	@functools.cached_property
	def _codes(self):
		return list(self.rows.keys())

	def _error(self, key):
		cat = self.category if self.category else 'this'
		if isinstance(key, str):
			raise KeyError(f"{key} is not a component of {cat} table") from None
		elif isinstance(key, int):
			raise IndexError(f"{key}. {cat} table has {len(self)} rows") from None
		else:
			raise TypeError(f"{type(key)}. can only be str or int")

	# make the table is immutable, as they are meant to represent published tables
	# taken from
	#	https://www.python.org/dev/peps/pep-0351
	def _immutable(self, *args, **kwargs):
		raise TypeError("Tables are immutable")

	__setitem__ = _immutable
	__delitem__ = _immutable
	clear = _immutable
	update = _immutable
	setdefault = _immutable
	pop = _immutable
	popitem = _immutable
