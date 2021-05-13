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
	""" """
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
	""" """
	def get_level(obj):
		return obj.__getattribute__(level)

	# iterate through collection to first record where breakpoints are
	breaks = []
	for idx, obj in enumerate(objs):
		if not get_level(obj):
			breaks.append(idx)

	# after locating the partition point for the objects, sort
	forest =[]
	for idx, brk in enumerate(breaks):
		try:
			section = objs[slice(brk, breaks[idx+1])]
		except IndexError:
			section = objs[slice(brk, len(objs))]

		tree = construct_tree(section, level, lower)
		forest.append(tree)

	return forest
