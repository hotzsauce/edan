"""

"""
from __future__ import annotations

import pathlib
import json
import funnelmap as fmap


# getting the existing paths to the already retreived jsons
warehouse = pathlib.Path(__file__).parent / 'warehouse'

stored_maps = []
for child in warehouse.iterdir():
	if child.suffix == '.json':

		with open(child, 'r') as json_file:
			local_mapping = json.load(json_file)
		stored_maps.append(local_mapping)



measures = ['quantity', 'price', 'nominal', 'real']
def sniff_sources(mappings: dict):
	"""
	read & return the source APIs that have codes stored in this mapping
	"""
	first_key = list(mappings.keys())[0]
	first_entry = mappings[first_key]

	for meas in measures:
		try:
			mdict = first_entry[meas]
			return list(mdict.keys())
		except KeyError:
			pass


def aliases_by_source(source: str) -> FunnelMap:
	"""
	given a source name ('bea', 'fred', 'av'), construct a single mapping
	of all the aliases in all the stored JSONs that point towards identifiers
	of that source API.

	Parameters
	----------
	source : str {'bea', 'fred', 'av'}
		the source API

	Returns
	-------
	FunnelMap
	"""

	if source not in {'bea', 'fred', 'av'}:
		raise ValueError(f"{repr(source)} not a recognized source API yet")

	# only want to use mappings that have ids for 'source' API
	src_mappings = []
	for mapping in stored_maps:

		if source in sniff_sources(mapping):
			src_mappings.append(mapping)

	alias_dict = {}
	for src_map in src_mappings:
		for src_info in src_map.values():
			for meas in measures:

				try:
					# some series don't have certain measures; e.g. Net Exports
					#	doesn't have quantity or price indices
					mdict = src_info[meas].copy()

					id_ = mdict.pop(source)
					aliases = [al for al in mdict.values()]

					if id_ in alias_dict:
						alias_dict[id_].extend(aliases)
					else:
						alias_dict[id_] = aliases

				except KeyError:
					pass

	return fmap.FunnelMap(alias_dict, strict=False)
