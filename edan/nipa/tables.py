"""
module for tables of NIPA components. the NIPATable object functions as a
mapping from series codes (the edan codes) to the components themselves
"""

from __future__ import annotations

import os
from copy import deepcopy



class TableIterator(object):
	"""
	iterator constructor for the NIPATable class. we split the iterator and the
	data container following mgilson's comment in the thread
	https://stackoverflow.com/questions/21665485/how-to-make-a-custom-object-iterable
	which in turn is apparently based on what Python does under the hood

	iterating over a NIPATable returns the names of the series in it
	"""

	def __init__(self, names: Iterable):
		self.idx = 0
		self.data = names

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self.data[self.idx+1]
		except IndexError:
			self.idx = 0
			raise StopIteration



class TablePrettyPrinter(object):
	"""
	pretty print the contents of a NIPATable to the console
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




class NIPATable(object):
	"""
	representation of a table of economic data where each row is a variable that
	is either composed of subcomponents (that lie visually below it in the table),
	or is an 'elemental' series that has no subcomponents. access the Component
	object for each variable by indexing into the table:

		>>> tb = NIPATable(pce_components, 'PCE')
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

	each time the table is indexed into, a full deepcopy of the requested component,
	and all its subcomponents if applicable, is returned.
	"""

	def __init__(
		self,
		aggregates: list,
		category: str = 'NIPA'
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

	def __getitem__(self, key):
		return self.rows[key]

	def __iter__(self):
		return TableIterator(list(self.rows.keys()))

	def __repr__(self):
		return f"{self.category} Table"

	def __str__(self):
		printer = TablePrettyPrinter(self)
		return printer.print()
