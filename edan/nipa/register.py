"""
module for registering & saving NIPA components
"""

from __future__ import annotations

import json
import pathlib

import urllib.request as urequest


registry_filename = '.registry.json'
registry = pathlib.Path(__file__).parent / registry_filename



class ComponentRegistry(object):

	registry_file = registry

	def __init__(self, *args, **kwargs):
		with open(self.registry_file, 'r') as reg_list:
			# list of dict with series codes & subcomponents
			json_list = json.load(reg_list)

		self.registry = {d['code']: d for d in json_list}

	def __getitem__(self, key):
		return self.registry[key]

	def __repr__(self):
		return 'ComponentRegistry'


registry = ComponentRegistry()
