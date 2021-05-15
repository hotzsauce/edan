"""
some algorithms for working with various graph-, and specifically, tree-,
like structures that are common in edan
"""

from __future__ import annotations

def construct_tree(
	objs: Iterable,
	level: str = 'level',
	lower: str = 'subs'
):
	"""
	construct an aggregation tree from an ordered collection of economic variables.
	the objects are ordered such that if object B follows object A, object B either
	aggregates directly into A, or B and A both aggregate into the same super-
	component. the objects are assumed to store the aggregation level & a record of
	the components that aggregate into it.

	Parameters
	----------
	objs : Iterable
		an ordered collection of economic variables
	level : str ( = 'level' )
		the attribute name that stores the level of aggregation this economic
		variable is at
	lower : str ( = 'subs' )
		the attribute name that stores the sub-components of this economic
		variable. assumed to have an `append` method

	Returns
	-------
	the first obj in `objs`, with it's `subs` attribute filled
	"""
	def get_level(obj):
		return obj.__getattribute__(level)

	def get_lower(obj):
		return obj.__getattribute__(lower)

	stack = [objs[0]]
	for i in range(1, len(objs)):

		obj = objs[i]
		sup = stack[-1]

		if get_level(obj) > get_level(sup):
			lower_objs = get_lower(sup)
			lower_objs.append(obj)
			stack.append(obj)

		else:
			top = stack.pop()
			while get_level(obj) <= get_level(top):
				top = stack.pop()

			lower_objs = get_lower(top)
			lower_objs.append(obj)

			stack.append(top)
			stack.append(obj)

	return stack[0]


def construct_forest(
	objs: Iterable,
	level: str = 'level',
	lower: str = 'subs'
):
	"""
	construct a list of aggregate economic variables with their sub-components
	assigned from an ordered list of components

	Parameters
	----------
	objs : Iterable
		an ordered collection of economic variables
	level : str ( = 'level' )
		the attribute name that stores the level of aggregation this economic
		variable is at
	lower : str ( = 'subs' )
		the attribute name that stores the sub-components of this economic
		variable. assumed to have an `append` method

	Returns
	-------
	a list of top-level aggregates
	"""
	def get_level(obj):
		return obj.__getattribute__(level)

	# iterate through collection to first record where breakpoints are
	breaks = []
	for idx, obj in enumerate(objs):
		if not get_level(obj):
			breaks.append(idx)

	# after locating the partition point for the objects, sort
	forest = []
	for idx, brk in enumerate(breaks):
		try:
			section = objs[slice(brk, breaks[idx+1])]
		except IndexError:
			section = objs[slice(brk, len(objs))]

		tree = construct_tree(section, level, lower)
		forest.append(tree)

	return forest
