"""
generic plotting classes shared across the different plot accessors
"""

from __future__ import annotations
from copy import deepcopy

import pandas as pd

from edan.utils.ts import (
	infer_freq,
	infer_freq_by_series
)
from edan.utils.dtypes import iterable_not_string

class GenericPlotAccessor(object):

	def __init__(self, *args, **kwargs):
		pass

	def manage_interpolation(
		self,
		data: pd.DataFrame,
		method: Union[str, dict] = 'linear'
	):
		"""
		interpolate the data, if need be. this method is associated with the
		GenericPlotManager, as opposed to the PlotDataManager, because the need
		to interpolate the data is due to plotting limitations (pandas interprets
		NaNs as breaks in lines), and not because of any data manipulations

		Parameters
		----------
		data : pandas DataFrame
			data to be interpolated
		method : str | dict, optional ( = 'linear' )

		Returns
		-------
		pandas DataFrame
		"""

		try:
			keys = list(method.keys())
			interp = method.pop(keys[0])
			return data.interpolate(method=interp, **method)

		except AttributeError:
			return data.interpolate(method=method)


class PlotDataManager(object):

	# if `periods` isn't provided, we provide default number of observations
	#	to show. annual data shows 12 years of it, otherwise show 5
	_default_periods = {
		'A': 12, 'Q': 20, 'M': 60, 'W': 260, 'D': 365*5
	}

	def __init__(self, objs: Iterable[EdanObject]):
		self.objs = [deepcopy(obj) for obj in objs]


	def select_containers(self, attr: str):
		"""
		in the case that self.objs don't hold the data themselves, but instead
		hold containers of the data, (e.g. a Component object will hold NIPASeries
		in one of the attrs in {'quantity', 'price', 'nominal', 'real'}, which
		in turn store data) we save references to those containers that
		are held in `obj.attr` for all the objects in self.objs

		Parameters
		----------
		attr : str
			the attribute name of the ogjects in self.objs that stores the
			underlying data
		"""
		self._containers = list()
		for obj in self.objs:
			self._containers.append(getattr(obj, attr))


	def merge_print_data(self, objs):
		"""
		concatenate an iterable of pandas Series/DataFrames together into the
		final DataFrame that will be printed. observations where all series are
		NaN are dropped.

		Parameters
		----------
		objs : Iterable[pandas Series, pandas DataFrame]
			data to be merged together

		Returns
		-------
		None
		"""
		self.print_data = pd.\
			concat(objs, axis='columns', join='outer').\
			dropna(axis='index', how='all')


	def truncate(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0
	):
		"""
		truncate the print data. all three of the parameters are optional in the
		`.plot()` method, so we do make some assumptions about their default
		values, in a case-by-case basis:

			1) [start not provided], [end not provided], [periods not provided]
				last observation printed is the final observation of dataset.
				number of periods printed is set according to _default_periods:
					self._default_periods = {
						'A': 12, 'Q': 20, 'M': 60, 'W': 260, 'D': 365*5
					}

			2) [start not provided], [end not provided], [periods provided]
				last observation printed is the final observation of dataset.
				number of periods printed is `periods`

			3) [start provided] or [end provided], [periods not provided]
				the endpoint of the printing dataset is determined by either
				`start` or `end`, and the number of periods provided is
				set according to _default_periods

			4) [start provided] or [end provided], [periods provided]
				the endpoint of the printing dataset is determined by either
				`start` or `end`, and the number of periods printed is `periods`

			5) [start provided] and [end provided]
				the printing dataset is bound by `start` and `end`. if provided,
				`periods` is ignored. this last point differs from the pandas
				`date_range` method, from which we cues for this method

			6) [periods == 'all']
				every observation is printed, regardless of the provided values
				of `start` and `end`

		Parameters
		----------
		start : str | bool | datetime-like, optional ( = '' )
			the first observation to be included in the printing dataset
		end : str | bool | datetime-like, optional ( = '' )
			the last observation to be included in the printing dataset
		periods : int | str, optional ( = 0 )
			the number of periods to be included in the printing dataset

		Returns
		-------
		pandas DataFrame
		"""
		df = self.print_data

		if not periods:
			# if periods is 0, use the default value according to frequency
			freqstr = infer_freq(df)
			if freqstr:
				periods = self._default_periods[freqstr]
			else:
				# couldn't infer frequency for some reason, use the more general method
				freqs = infer_freq_by_series(df)

				# if series are of different frequencies, default to showing the
				#	number of periods of the highest freq
				periods_by_series = [self._default_periods[f] for f in freqs]
				periods = max(periods_by_series)

		elif isinstance(periods, str):
			# print all periods
			if periods.lower().strip() == 'all':
				return df
			else:
				raise ValueError("the only accepted str value of 'periods' is 'all'")

		if start and end:
			if isinstance(start, bool):
				start = df.first_valid_index()
			if isinstance(end, bool):
				end = df.last_valid_index()
			return df.loc[start:end]

		elif start:
			if isinstance(start, bool):
				start = df.first_valid_index()
			return df.loc[start:].iloc[:periods]

		elif end:
			if isinstance(end, bool):
				end = df.last_valid_index()
			return df.loc[:end].iloc[-periods:]

		else:
			end = df.last_valid_index()
			return df.loc[:end].iloc[-periods:]

		msg = (
			f"unable to interpret plotting dataset from 'start': {repr(start)}, "
			f"'end': {repr(end)}, 'periods': {repr(periods)}."
		)
		raise ValueError(msg)


	def series_names(self, names: Union[str, list] = '', *args):
		"""
		create a list of series name to display in the plot legend. the names
		are based on information stored in the `containers` or `objs` attribute.

		Parameters
		----------
		names : str | list ( = '' )
			if not provided, the stored human-readable names will be used in
			the legend. additional identifiers are appended to each legend
			entry through the `args` parameter. if `names` is a list, that list
			is returned without alteration. if `names = 'codes'`, the `edan`
			code is used.
		args : positional arguments
			terms to add to each entry of `names` if it's not provided

		Returns
		-------
		list
		"""
		if names == 'codes':
			# using `edan` codes of data containers
			return [c.code for c in self.containers]

		elif iterable_not_string(names):
			# don't edit any provided names
			return names

		elif not names:
			# if `names` is not provided, use the saved human-readable names
			objs = self.objs
			name_list = list()
			for obj in objs:

				entry = obj.short_name
				if entry == '':
					entry = obj.long_name

				for arg in args:
					entry += f" {arg.capitalize()}"

				name_list.append(entry)

			return name_list

		raise ValueError(f"cannot interpret legend entries: {repr(names)}")


	@property
	def containers(self):
		if hasattr(self, '_containers'):
			return self._containers
		else:
			return self.objs
