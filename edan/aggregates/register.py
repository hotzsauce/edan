"""
module for registering & saving Components
"""

from __future__ import annotations

import json


class ComponentRegistry(object):

	def __init__(self, reg_file: Union[str, pathlib.Path], concept=''):
		self.reg_file = reg_file
		self.concept = concept

		with open(self.reg_file, 'r') as reg_list:
			# list of dict with series codes & subcomponents
			json_list = json.load(reg_list)

		self.registry = {d['code']: d for d in json_list}

	def __getitem__(self, key):
		return self.registry[key]

	def __repr__(self):
		return f'ComponentRegistry({self.concept})'
