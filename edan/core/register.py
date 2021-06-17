"""
module for registering & saving Components
"""

from __future__ import annotations

import json
import pathlib

# create registry based on JSON in edan/core/
registry_filename = '.registry.json'
registry_file = pathlib.Path(__file__).parent / registry_filename


class ComponentRegistry(object):

	reg_file = registry_file

	def __init__(self):

		with open(self.reg_file, 'r') as reg_list:
			# list of dict with series codes & subcomponents
			json_list = json.load(reg_list)

		self.registry = {d['code']: d for d in json_list}

	def __getitem__(self, key):
		return self.registry[key]

	def by_concept(self, concept: str):
		return (e for e in self.registry.values() if e['__concept__'] == concept)

	def by_table(self, table: str):
		return (e for e in self.registry.values() if e['__table__'] == table)

	def by_ctype(self, ctype: str):
		return (e for e in self.registry.values() if e['__ctype__'] == ctype)


registry = ComponentRegistry()
