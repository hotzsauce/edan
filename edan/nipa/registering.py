"""
module for registering Components
"""

from __future__ import annotations

import json
import pathlib

from edan.nipa.components import (
	Component
)


cd = pathlib.Path(__file__).parent
registry_filename = 'registry.json'
registry_loc = cd / registry_filename


class ComponentEncoder(json.JSONEncoder):
	"""
	class for writing & recording Component classes to the json registry
	"""
	def default(self, obj):
		if isinstance(obj, Component):
			return {
				'__component__': True,
				'name': obj.name,
				'level': obj.level_code,
				'price': obj.price_code,
				'subs': obj._subs,
				'sups': obj._sups,
				'long_name': obj.long_name,
				'short_name': obj.short_name
			}

		# let the base class default method raise the TypeError
		return json.JSONEncoder.default(self, obj)


class ComponentDecoder(json.JSONDecoder):
	"""
	class for reading & creating Components from the json registry
	"""

	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

	def object_hook(self, dct):
		try:
			if dct['__component__']:
				return Component.from_json(dct)
			else:
				raise NotImplementedError(f"Unable to decode entry {dct}")

		except KeyError:
			raise ValueError(dct)


def encode_registry(comp_list: List[Component]):
	"""
	writes a list of Component objets to the GDP component registry

	Parameters
	----------
	comp_list : list of Component objects

	Returns
	-------
	None
	"""

	with open(registry_loc, 'w') as new_file:
		json.dump(comp_list, new_file, cls=ComponentEncoder, indent=4)


def decode_registry(*args, **kwargs):
	"""
	read in the registry of GDP components & interpret them as Component objects

	Returns
	-------
	list of Component objects
	"""

	try:
		with open(registry_loc, 'r') as old_file:
			try:
				comp_list = json.load(old_file, cls=ComponentDecoder)
			except ValueError:
				# if empty, simplejson.decoder.JSONDecodeError (which
				#	inherits from ValueError) is raised
				comp_list = list()

	except FileNotFoundError:
		registry_loc.touch()
		comp_list = list()

	return comp_list


def empty_registry(*args, **kwargs):
	"""
	clears all contents of the `registry.json` file. Use outside of development
	is not expected, but it's handy to have while I'm working on this
	"""

	try:
		open(registry_loc, 'w').close()

	except FileNotFoundError:
		registry_loc.touch()


def register_component(comp: Component):
	"""
	write a Component to the GDP registry. a ValueError is thrown if `comp`
	already exists in the registry

	Parameters
	----------
	comp : Component
		a Component object
	"""

	comp_list = decode_registry()

	if comp_list:
		if comp.name in [c.name for c in comp_list]:
			raise ValueError(
				f"Component {repr(comp.name)} is already registered - to "
				"update this component use the `edan.gdp.update_registry` method"
			)

	# add the new component and sort the list. I can't imagine there being
	#	more than a few hundred GDP Components (at most) ever being in the 
	#	registry, so I'm not too concerned about efficiency in this case
	comp_list.append(comp)
	comp_list.sort(key=lambda c: c.name)

	encode_registry(comp_list)


def update_registry(
	obj: Union[Component, str],
	**kwargs
):
	"""
	update a component's information in the registry

	Parameters
	----------
	obj : Component | str
		the Component, or name of the Component, to be updated. If the Component
		is not extant in registry, a ValueError is thrown
	kwargs : keyword arguments
		the Component information that will be updated. the key(s) must be one
		of 'level', 'price', 'subs', or 'sup', and the values will be the new
		information to be recorded

	Returns
	-------
	None
	"""

	comp_list = decode_registry()

	try:
		comp_name = obj.name
	except AttributeError:
		comp_name = obj

	# make sure this Component already exists
	if comp_list:
		existing_comp_names = [c.name for c in comp_list]
		if comp_name not in existing_comp_names:
			raise ValueError(
				f"Component {repr(comp_name)} cannot be updated - first register "
				"it using the `edan.gdp.register_component` method"
			)
	else:
		raise ValueError("No existing Components to update")

	# get existing Component and update the data
	comp = comp_list[existing_comp_names.index(comp_name)]
	json_maps = {
		'level': 'level_code', 'price': 'price_code',
		'subs': '_subs', 'sup': '_sup'
	}
	for k, v in kwargs.items():
		setattr(comp, json_maps[k], v)

	# write new json file
	encode_registry(comp_list)
