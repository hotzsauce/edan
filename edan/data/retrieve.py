"""
retrieving data from API sources & storing it in the local data warehouse
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

from edan.data.aliases import alias_maps


warehouse = pathlib.Path(__file__).parent / 'warehouse'



class EdanDataRetriever(object):

	def __init__(self):
		pass

	def retrieve(
		self,
		code: str,
		source: str = '',
		*init_args, **init_kwargs
	):
		"""
		retrieve and return both economic data and metadata for data series
		corresponding to `code`. if this data has already been retrieved from
		the appropriate fetcher, then the saved data is read in & from the
		parquet files in the data/warehouse directory. if not, the fetcher
		uses the API to pull the data, which is then formatted to be consistent
		with the `edan` data style, then saved, then finally both the data and
		metadata are returned.

		Parameters
		----------
		code : str
			the code referencing the desired series. the alias maps are checked
			in case the provided `code` is an alias
		source : str ( = '' )
			the source api that hosts the series' data & metadata. built-in
			sources are FRED (mortadata/fredapi), BEA (hotzsauce/beapy), and
			AlphaVantage (RomelTorres/alpha_vantage). although this parameter
			is not required as per the method definition, doing a blind retrieval
			on all the saved fetchers is not implemented yet
		*init_args : positional arguments
			initialization arguments in case the source API key is not saved
		*init_kwargs : keyword arguments
			initialization arguments in case the source API key is not saved

		TODO
		----
			- blind retrieval when `source` is not provided
			- AlphaVantage API

		Returns
		-------
		2-tuple of pandas DataFrame
			data, metadata
		"""

		# if this code doesn't need to be translated, return immediately
		if code in inventory:
			return self.retrieve_from_warehouse(code)

		# retrieve the 'official' identifier in case this code is an alias
		fm = alias_maps[source]
		try:
			code = fm[code]
		except KeyError:
			# `code` might be a code I haven't constructed a crosswalk for
			pass


		# retrieving stored data or fetching from API
		if code in inventory:
			return self.retrieve_from_warehouse(code)

		if source:
			fetcher = fetchers_by_source[source]

			if isinstance(fetcher, type):
				# this fetcher hasn't been initialized yet. use provided
				#	initialization args & kwargs
				fetcher = fetcher(*init_args, **init_kwargs)
				fetchers_by_source[source] = fetcher

			data, meta = fetcher.fetch(code)
			self.save_fetched_info_to_warehouse(data, meta)
			return data, meta

		raise NotImplementedError("cannot retrieve without `source` yet")


	def retrieve_from_warehouse(self, code: str):
		"""
		retrieve & return the economic & meta data from the parquet files
		in the warehouse

		Parameters
		----------
		code : str
			data series identifier
		"""
		# retrieving data
		source, freq = inventory[code]
		path = warehouse / source / f'{freq}.parquet'
		data = self.load_parquet(path, columns=[code])

		path = warehouse / source / 'metadata.parquet'
		meta = self.load_parquet(path, columns=[code])

		return data, meta

	def retrieve_data(
		self,
		code: str,
		source: str = '',
		*init_args, **init_kwargs
	):
		data, meta = self.retrieve(code, source, *init_args, **init_kwargs)
		return data.squeeze().dropna(axis='index', how='all')

	def retrieve_metadata(
		self,
		code: str,
		source: str = '',
		*init_args, **init_kwargs
	):
		data, meta = self.retrieve(code, source, *init_args, **init_kwargs)
		return meta.squeeze()

	def save_fetched_info_to_warehouse(
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
