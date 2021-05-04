"""
module for recording & retrieving data series, api sources, and frequencies
"""

import json
import pathlib

# directory that contains the JSON of series information
data_dir = pathlib.Path(__file__).parent
inv_file = '.inventory.json'


class EdanInventory(object):

	inventory_path = data_dir / inv_file

	def __init__(self):

		# create inventory if it doesn't exist
		self.inventory_path.touch(exist_ok=True)

		with open(self.inventory_path, 'r') as inv_file:
			try:
				inv_list = json.load(inv_file)
			except json.decoder.JSONDecodeError:
				# in case inv_file is empty
				inv_list = []

		self.inv_maps = {}
		for dct in inv_list:
			source, freq = dct['source'], dct['freq']
			self.inv_maps[dct['code']] = (source, freq)

	def __contains__(self, code: str):
		return code in self.inv_maps

	def __getitem__(self, code: str):
		try:
			return self.inv_maps[code]
		except KeyError:
			raise KeyError(
				f"{repr(code)} is not a saved series code"
			) from None

	def write_updated_inventory(self):
		"""write new data series information to inventory file"""

		inv_list = []
		for code, info in self.inv_maps.items():
			dct = {'code': code, 'source': info[0], 'freq': info[1]}
			inv_list.append(dct)

		with open(self.inventory_path, 'w') as inv_file:
			json.dump(inv_list, inv_file, indent=4)

	def add_to_inventory(self, code: str, source: str, freq: str):
		self.inv_maps[code] = (source, freq)
		self.write_updated_inventory()

inventory = EdanInventory()
