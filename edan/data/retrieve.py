"""

"""

from __future__ import annotations

import json
import pathlib
import pandas as pd

from edan.data.inventory import inventory
from edan.data.fetchers import (
	EdanFetcher,
	fetchers_by_source
)

warehouse = pathlib.Path(__file__).parent / 'warehouse'



class EdanDataRetriever(object):

	def __init__(self):
		pass

	def retrieve_data(self, code: str, source: str = ''):

		if code in inventory:
			return self.retrieve_data_from_warehouse(code)

		if source:
			fetcher = fetchers_by_source[source]

			data, meta = fetcher.fetch(code)
			self.save_fetched_data_to_warehouse(data, meta)
			return data.squeeze().dropna(axis='index', how='all')

		return self.retrieve_data_no_source(code)

	def retrieve_data_from_warehouse(self, code: str):
		"""
		retrieve & return economic data from parquet file in the warehouse

		Parameters
		----------
		code : str
			data series identifier
		"""
		source, freq = inventory[code]
		path = warehouse / source / f'{freq}.parquet'
		data = self.load_parquet(path, columns=[code])

		return data.squeeze().dropna(axis='index', how='all')

	def retrieve_data_no_source(self, code: str):
		"""
		retrieve & store economic data & associated metadata from the source API,
		and return the data Series

		Parameters
		----------
		code : str
			data series identifier
		"""
		for fetcher in fetchers_by_source.values():
			try:
				data, meta = fetcher.fetch(code)
				self.save_fetched_data_to_warehouse(data, meta)
				return data.squeeze().dropna(axis='index', how='all')
			except:
				pass

	def retrieve_metadata(self, code: str, source: str = ''):
		if code in inventory:
			return self.retrieve_metadata_from_warehouse(code)

		if source:
			fetcher = fetchers_by_source[source]

			data, meta = fetcher.fetch(code)
			self.save_fetched_data_to_warehouse(data, meta)
			return meta.squeeze()

		return self.retrieve_metadata_no_source(code)

	def retrieve_metadata_from_warehouse(self, code: str):
		"""
		retrieve & return metadata from parquet file in the warehouse

		Parameters
		----------
		code : str
			data series identifier
		"""
		source, _ = inventory[code]
		path = warehouse / source / 'metadata.parquet'
		meta = self.load_parquet(path, columns=[code])

		return meta.squeeze()

	def retrieve_metadata_no_source(self, code: str):
		"""
		retrieve & store economic data & associated metadata from the source API,
		and return the metadata Series

		Parameters
		----------
		code : str
			data series identifier
		"""
		for fetcher in fetchers_by_source.values():
			try:
				data, meta = fetcher.fetch(code)
				self.save_fetched_data_to_warehouse(data, meta)
				return meta.squeeze()
			except:
				pass

		raise ValueError(f"{repr(code)} is not recognized by any saved Fetcher")

	def save_fetched_data_to_warehouse(
		self,
		data: Series,
		meta: Series
	):
		"""
		save data and metadata to the data warehouse, and store its code
		identifier, source api, and frequency to the inventoy JSON.

		Parameters
		----------
		data : pandas Series
			the economic data to save locally
		meta : pandas Series
			the metadata of the series. must have 'source' and 'frequency' entries
		"""

		if ('source' not in meta.index) or ('frequency' not in meta.index):
			raise ValueError(
				"metadata index must contain 'source' and 'frequency' entries. "
				"edit Fetcher method `format_metadata` to fix this."
			)

		# information necessary to retrieve/create correct parquet files
		code = meta.name
		source = meta.loc['source']
		freq = meta.loc['frequency'].lower()

		# saving the economic data
		data_path = warehouse / source / f'{freq}.parquet'
		old_data = self.load_parquet(data_path)
		if old_data is None:
			# first data series of this frequency
			self.write_parquet(data, data_path)

		else:
			df = pd.concat((old_data, data), axis='columns')
			self.write_parquet(df, data_path)

		# saving the metadata
		meta_path = warehouse / source / 'metadata.parquet'
		old_meta = self.load_parquet(meta_path)
		if old_meta is None:
			# first data series of this source
			self.write_parquet(meta, meta_path)

		else:
			df = pd.concat((old_meta, meta), axis='columns')
			self.write_parquet(df, meta_path)

		# record data series info for future accessing
		inventory.add_to_inventory(code, source, freq)

	def write_parquet(
		self,
		data: Union[Series, DataFrame],
		file_path: Union[str, Path]
	):
		"""
		write a Series or DataFrame to a parquet file. nice to have because
		pandas Series do not have a `to_parquet` method

		Parameters
		----------
		data : pandas Series or DataFrame
		file_path : str or path-like
		"""
		if isinstance(data, pd.Series):
			data.to_frame().to_parquet(file_path)
		else:
			data.to_parquet(file_path)

	def load_parquet(self, file_path: Union[str, Path], **kwargs):
		"""
		read in a parquet file that may or may not exist yet

		Parameters
		----------
		file_path : str or path-like
		"""
		if isinstance(file_path, str):
			file_path = pathlib.Path(file_path)

		if file_path.exists():
			df = pd.read_parquet(file_path, **kwargs)
			return df

		else:
			return None

retriever = EdanDataRetriever()
