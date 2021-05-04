"""
module for recording, retrieving, and updating API keys needed to fetch
economic data
"""

import json
import pathlib



# directory containing the JSON of API keys & filename that stores that JSON
data_dir = pathlib.Path(__file__).parent
keychain_file = '.api_keys.json'



class APIKeyChain(object):

	keychain_path = data_dir / keychain_file

	def __init__(self):

		# create keychain record if it doesn't exist
		self.keychain_path.touch(exist_ok=True)

		with open(self.keychain_path, 'r') as key_file:
			try:
				key_list = json.load(key_file)
			except json.decoder.JSONDecodeError:
				# in case key_file is empty
				key_list = []

		self.api_keys = {}
		for api in key_list:
			s, k = api['source'], api['key']
			self.api_keys[s] = k

	def write_updated_keychain(self):
		"""write new API sources and keys to keychain file"""

		key_list = []
		for source, key in self.api_keys.items():
			api_dict = {'source': source, 'key': key}
			key_list.append(api_dict)

		with open(self.keychain_path, 'w') as key_file:
			json.dump(key_list, key_file, indent=4)

	def add_to_keychain(self, source: str, key: str):
		self.api_keys[source] = key
		self.write_updated_keychain()

	def __getitem__(self, source: str):
		"""retrieve the saved API key based on the source name"""
		try:
			return self.api_keys[source]
		except KeyError:
			raise KeyError(
				f"{repr(source)} is not a saved API source entity"
			) from None


keychain = APIKeyChain()



def add_api_key(source: str, key: str):
	"""
	add a new API source and key to the saved list of keys

	Parameters
	----------
	source : str
		the name of the entity hosting the API data
	key : str
		the user-assigned login key for the API
	"""
	keychain.add_to_keychain(source, key)

def retrieve_api_key(source: str):
	"""
	retrieve saved API key given the source name

	Parameters
	----------
	source : str
		the name of the entity hosting the API data
	"""
	return keychain[source]

def update_api_key(source: str, key: str):
	"""
	update an API key by source

	Parameters
	----------
	source : str
		the name of the entity hosting the API data
	key : str
		the API key for `source`
	"""
	keychain.add_to_keychain(source, key)
