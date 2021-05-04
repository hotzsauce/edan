"""
module for the base Fetcher class
"""

from __future__ import annotations

import pathlib
import pandas as pd

from edan.data.api_keys import retrieve_api_key

warehouse = pathlib.Path(__file__).parents[1] / 'warehouse'


class EdanFetcher(object):
	"""
	base class with shared methods for data fetchers
	"""

	subclass_msg = "'{method}' must be implemented by subclass of EdanFetcher"

	def __init__(self, source: str, source_api: API, source_key: str = ''):
		# retrieve source key if not provided
		if not source_key:
			source_key = retrieve_api_key(source)

		self.source = source
		self.api = source_api(source_key)

		self.source_dir = warehouse / self.source
		self.source_dir.mkdir(exist_ok=True)

	def __str__(self):
		return f"{type(self).__name__}"

	def fetch(self, *args, **kwargs):
		""" """
		msg = self.subclass_msg.format(method='fetch')
		raise NotImplementedError(msg)

	def format_data(self, *args, **kwargs):
		""" """
		msg = self.subclass_msg.format(method='format_data')
		raise NotImplementedError(msg)

	def format_metadata(self, *args, **kwargs):
		""" """
		msg = self.subclass_msg.format(method='format_metadata')
		raise NotImplementedError(msg)

	@property
	def date_fetched(self):
		return pd.Timestamp.now()
