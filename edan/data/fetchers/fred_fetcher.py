"""

"""
from __future__ import annotations

import pandas as pd
from fredapi import Fred

from edan.data.fetchers.base import EdanFetcher



class FredFetcher(EdanFetcher):

	def fetch(self, code: str):
		""" """
		data_raw = self.api.get_series(code)
		data = self.format_data(data_raw, code)

		meta_raw = self.api.get_series_info(code)
		meta = self.format_metadata(meta_raw, code)

		return data, meta

	def format_data(self, data: Series, code: str):
		data.name = code
		return data

	def format_metadata(self, meta: Series, code: str):
		""" """
		# format date_fetched in the same way FRED formats other dates
		additional_meta = pd.Series(
			[self.date_fetched.strftime('%Y-%m-%d'), 'fred'],
			index=['date_fetched', 'source']
		)
		metadata = meta.append(additional_meta)
		metadata.name = code
		return metadata

	def __init__(self, api_key: str = ''):
		# initialize Fred class in `api` attribute
		super().__init__('fred', Fred, api_key)
