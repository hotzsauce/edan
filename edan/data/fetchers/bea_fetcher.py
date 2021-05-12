"""
fetcher for Bureau of Economic Analysis data
"""

from __future__ import annotations

import pandas as pd
from beapy import BEA

from edan.data.fetchers.base import EdanFetcher


# the highest frequency available for each dataset. I don't think BEA's API
#	(not beapy, but BEA's API) has a way to select this
dataset_frequencies = {
	'niunderlyingdetail': 'monthly',
	'nipa': 'quarterly'
}

class BeaFetcher(EdanFetcher):

	def fetch(self, code: str):

		dataset, table_name, series_name = code.split('!')

		# always want to save the most frequent version
		frequency = dataset_frequencies[dataset]

		# now that frequency is known, retrieve data
		res = self.api.data(
			dataset,
			tablename=table_name,
			series_code=series_name,
			frequency=frequency,
			year=2020 # X retrieves all years
		)

		# BEA accepts a `series_name` parameter in their API call, but can only
		#	ever return the entire dataset
		series = res.data[series_name.upper()]
		data = self.format_data(series, code)

		metadata = res.metadata.loc[series_name.upper()]
		meta = self.format_metadata(metadata, code, frequency)

		return data, meta

	def format_data(self, data: Series, code: str):

		# index is one of {'yyyyMmm', 'yyyyQq', 'yyyy'}
		freq = data.index.to_frame(name='string')

		freq['M'] = freq.string.str.contains('M')
		freq['Q'] = freq.string.str.contains('Q')
		freq['A'] = ~(freq['M'] | freq['Q'])

		# get "ValueError: 'q' is a bad directive in format '%YQ%q' for quarterly
		#	data when 'Q': '%YQ%q' is the mapping in `freq_fmts`? so we need to
		#	change that string before formatting
		freq_fmts = {
			'M': '%YM%m',
			'Q': '%YM%m',
			'A': '%Y'
		}
		for f in freq_fmts.keys():
			idx = freq[f]
			if f == 'Q':
				yr = freq.string[idx].str[:4].astype(str)
				mo = 3 * freq.string[idx].str[-1].astype(int)

				fq = (yr + 'M').str.cat(mo.astype(str).str.zfill(2))
				freq.string[idx] = fq
			freq.loc[idx, 'dt'] = pd.to_datetime(freq.string[idx], format=freq_fmts[f])

		data.index = freq.dt
		data.index.name = ''
		data.name = code
		return data

	def format_metadata(self, meta: Series, code: str, freq: str):
		""" """
		additional_meta = pd.Series(
			[self.date_fetched.strftime('%Y-%m-%d'), 'bea', freq],
			index=['date_fetched', 'source', 'frequency']
		)
		metadata = meta.append(additional_meta)
		metadata.name = code
		return metadata

	def __init__(self, api_key: str = ''):
		# initialize BEA class in `api` attribute
		super().__init__('bea', BEA, api_key)
