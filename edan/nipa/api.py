"""
module that prepares the GDP component tree
"""

from __future__ import annotations

from copy import deepcopy

from edan.nipa.registering import decode_registry



#----------------------------
#	methods for filling in `_subs` attributes of components

def _fill_subcomponents(
	top_comp: Component,
	comp_dict: dict
):
	"""
	replace all the string Component names in the `_subs` attributes with actual
	sub-Component objects

	Parameters
	----------
	top_comp : Component
		the highest-level (in terms of economic aggregating) Component
	comp_dict : dict
		a dictionary of 'comp_name': `Component` form. it should have all the
		Components that aggregate into the top-level Component `top_comp`

	Returns
	-------
	Component
		the `top_comp` Component with its `_subs` attribute a list of Component
		objects, whose `_subs` attributes reference Components themselves
	"""
	subs = top_comp._subs
	subs_comps = list()

	for comp in subs:
		try:
			# in this case this sub-component name has already been replaced with
			#	its corresponding Component
			if comp._subs:
				subs_comps.append(_fill_subcomponents(comp_dict[comp.name], comp_dict))
			else:
				subs_comps.append(comp_dict[comp.name])

		except AttributeError:
			# `comp` is just the sub-component name
			if comp_dict[comp]._subs:
				subs_comps.append(_fill_subcomponents(comp_dict[comp], comp_dict))
			else:
				subs_comps.append(comp_dict[comp])

	top_comp._subs = subs_comps
	return top_comp


def assign_subcomponents(
	top_comp: str,
	comp_list: List[Component]
):
	"""
	prepares a list of Components to be assigned to the `_subs` attribute of an
	aggregate Component

	Parameters
	----------
	top_comp : str
		the name of a Component
	comp_list : list
		a list of Component objects

	Returns
	-------
	Component
		the Component corresponding to `top_comp`, with `_subs` replaced with
		a list of components
	"""
	comp_dict = {c.name: c for c in comp_list}

	try:
		comp = comp_dict[top_comp]
		tree = _fill_subcomponents(comp, comp_dict)
	except KeyError:
		raise ValueError(f"Unrecognized component name: {repr(top_comp)}") from None

	return tree


#----------------------------
#	preparing the top-level GDP component

# a list of gdp components with their `_subs` attribute a list of Component names
gdp_components = decode_registry()

# replace Component names with references to the Component objects
GDP = assign_subcomponents('gdp', gdp_components)



#----------------------------
#	preparing the GDP table of all GDP components

class TableIterator(object):
	"""
	iterator constructor for the _GDPTable class. we split the iterator and the
	data container following mgilson's comment in the thread
	https://stackoverflow.com/questions/21665485/how-to-make-a-custom-object-iterable
	which in turn is apparently based on what Python does under the hood.

	iterating over a _GDPTable returns the names of the components
	"""
	def __init__(self, names):
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


class _GDPTable(object):
	"""
	a record of all the GDP components that are stored in the registry. access
	the Component objects for each variable by indexing into the table:

		>>> tb = GDPTable()
		>>> tb['pce']
		Component[pce]

	following the class definition here, the table is initialized below without
	the leading underscore, i.e.

		>>> GDPTable = _GDPTable()

	which is what we see used in the above example. a collection of Components
	can be retrieved at once, too. the returned object will have the same type
	as the indexing key, as in

		>>> tb[['gdp', 'resinv']]
		[Component[gdp], Component[resinv]]

		>>> tb[('dur', 'struct', 'exp', 'nondur')]
		(Component[dur], Component[struct], Component[exp], Component[nondur])

	the names of all the components currently in the table are stored in the
	`names` property:

		>>> tb.names
		['bfi', 'def', 'dur', 'equip', ... ]

	if the Component registry is updated within a script using the
	`edan.gdp.register_component()` function, the extant table can be updated
	via the `tb.update_table()` method.
		iterating over the table is similar to iterating over a dictionary of
	the form 'name': Component; doing so yields an iterator of the component
	names:

		>>> for comp in tb:
		>>>		print(comp)
		bfi
		def
		dur
		...

	again taking the lead from the `dict` class, iterating over the names and
	associated components at the same time is accomplished by the `.items()`
	method:

		>>> for name, comp in tb.items():
		>>>		print(name, ': ', comp)
		bfi: Component[bfi]
		def: Component[def]
		dur: Component[dur]
		...

		it's important to note that each time the table is indexed into, a full
	deepcopy of the requested component, and all of its subcomponents if
	applicable, is returned. that is, in

		>>> pce1 = tb['pce']
		>>> pce2 = tb['pce']

	are stored in different locations in memory, and modifying any attributes of
	`pce1` (or any attributes of its subcomponents) will not affect any part of
	`pce2` (or any parts of its subcomponents).
	"""

	def __init__(self, *args, **kwargs):
		self.update_table()

	def update_table(self):
		"""reconstruct dict of form 'name': Component"""
		self.gdp_dict = {c.name: c for c in decode_registry()}

	def _single_get(self, key):
		comp = self.gdp_dict[key]
		filled = _fill_subcomponents(comp, self.gdp_dict)
		return deepcopy(filled)

	def __getitem__(self, key):
		"""
		retrieve a Component or collection of Component objects by name. if a
		collection, the returned type will be the same as `type(key)`.

		Parameters
		----------
		key : str | Iterable
			name of Component or collection of component names

		Returns
		-------
		Component or Iterable[Component]
		"""
		try:
			# single component name
			return self._single_get(key)

		except (TypeError, KeyError):
			# key is list, tuple, set, or other iterable
			objs = [self._single_get(k) for k in key]
			return type(key)(objs)

	def __iter__(self):
		return TableIterator(self.names)

	def items(self):
		_gdp_dict = {k: deepcopy(v) for k, v in self.gdp_dict.items()}
		return _gdp_dict.items()

	@property
	def names(self):
		"""names of all the components as a list"""
		return list(self.gdp_dict.keys())

	def __repr__(self):
		return '<GDPTable>'

GDPTable = _GDPTable()
