"""
module for functions of time series data of the Series
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.utils.ts import (
	infer_freq,
	periods_per_year
)


series_mods = dict()
def add_mod(key, func):
	series_mods[key] = func

add_mod('diff',		lambda s, n, h: s.diff(n))
add_mod('diff%',	lambda s, n, h: 100 * (s.divide(s.shift(n)) - 1))
add_mod('diffl',	lambda s, n, h: 100 * np.log(s.divide(s.shift(n))))
add_mod('difa',		lambda s, n, h: (h/n) * s.diff(n))
add_mod('difa%',	lambda s, n, h: 100 * ( s.divide(s.shift(n)) ** (h/n) - 1))
add_mod('difal',	lambda s, n, h: 100 * (h/n) * np.log(s.divide(s.shift(n))))
add_mod('difv',		lambda s, n, h: s.diff(n)/n)
add_mod('difv%',	lambda s, n, h: 100 * (s.divide(s.shift(n)) ** (h/n) - 1))
add_mod('difvl',	lambda s, n, h: (100/n) * np.log(s.divide(s.shift)))
add_mod('movv',		lambda s, n, h: s.rolling(n).mean())
add_mod('mova',		lambda s, n, h: h * s.rolling(n).mean())
add_mod('movt',		lambda s, n, h: s.rolling(n).sum())
add_mod('yryr',		lambda s, n, h: s.diff(h))
add_mod('yryr%',	lambda s, n, h: s.divide(s.shift(h)) - 1)
add_mod('yryrl',	lambda s, n, h: 100 * np.log(s.divide(s.shift(h))))


class ReIndexer(object):

	def __init__(self, base):
		"""initializing ReIndexer checks the various cases that 'base' can take"""
		if not base:
			raise ValueError("'base' must be provided to reindex data")

		try:
			# this will throw ValueError if 'base' is some sort of datetime-like str
			base_flt = float(base)

			if base_flt != int(base):
				raise TypeError("cannot interpret index 'base' of type 'float'")

			self.base = int(base)

		except ValueError:
			# 'base' is a datetime-list string
			try:
				date_base = pd.Timestamp(base)
			except ValueError:
				raise ValueError(
					f"unable to interpret index base: {repr(base)}"
			) from None

			self.base = date_base


	@property
	def data_freq(self):
		return infer_freq(self.data)


	def base_data_from_integer(self):
		"""
		if the re-indexing base period is just an integer, the reindexing value
		is the average of the entire year corresponding to 'base'

		Returns
		-------
		pandas Series
		"""
		rebase = self.data[self.data.index.year == self.base]

		if rebase.empty:
			name = self.data.name
			raise KeyError(f"'{name}' has no data in the year {self.base}")

		return rebase


	def base_data_from_datetime(self):
		"""
		if self.data is at a daily frequency, the self.base date must be in the
		index, or else a KeyError is thrown. if self.data is at any lower frequency
		(weekly, monthly, quarterly, annually), then the average of that frequency
		period that contains the self.base date is used

		Returns
		-------
		pandas Series
		"""
		freq = self.data_freq
		if freq == 'D':
			rebase = self.data.loc[self.base]
		else:
			df = self.data
			rebase = df.loc[(df.index >= self.base) & (df.index <= self.base)]

		return rebase


	def __call__(self, data):

		self.data = data

		if isinstance(self.base, int):
			rebase = self.base_data_from_integer()
		else:
			rebase = self.base_data_from_datetime()

		base_value = rebase.mean()

		return 100 * self.data / base_value


class ModificationAccessor(object):

	def __init__(self, obj, *args, **kwargs):
		self.data = obj.data

	def __call__(self,
		method: Union[str, Callable] = 'difa%',
		n: int = 1,
		h: int = 0,
		base: Union[str, TimeStamp] = '',
		*args, **kwargs
	):
		"""
		modify the data according to parameter `method`

		throughout these comments/docs, the conventions are:
			x(t)	: observation of time series x at time t
			h		: the number of observations of x per year
			n		: the additional user-given parameter

		Parameters
		----------
		method : str | callable
			specification of how data will be modified. recognized string values
			are:
				'diff'	: period-to-period difference
							x(t) - x(t-n)
				'diff%'	: period-to-period percent change
							100 * [ (x(t)/x(t-n)) - 1 ]
				'diffl' : period-to-period log change
							100 * ln[ x(t)/x(t-n) ]
				'difa'	: period-to-period annualized change
							(h/n) * [ x(t) - x(t-n) ]
				'difa%'	: period-to-period annualized percent change
							100 * [ (x(t)/x(t-n))^(h/n) - 1 ]
				'difal' : period-to-period annualized log change
							100 * (h/n) * ln[ x(t)/x(t-n) ]
				'difv'	: period-to-period average difference change
							[ x(t) - x(t-n) ]/n
				'difv%'	: period-to-period average percent change
							100 * [ (x(t)/x(t-n))^(h/n) - 1 ]
				'difvl'	: period-to-period average log change
							(100/n) * ln[ x(t)/x(t-n) ]
				'movv'	: n-period moving average
							sum_{j=0}^{n-1} x(t-j)/n
				'mova'	: n-period annualized moving average
							sum_{j=0}^{n-1} x(t-j) * (h/n)
				'movt'	: n-period moving total
							sum_{j=0}^{n-1} x(t-j)
				'yryr'	: year-over-year change
							x(t) - x(t-h)
				'yryr%'	: year-over-year percent change
							[ x(t)/x(t-h) ] - 1
				'yryrl' : year-over-year log change
							100 * ln[ x(t)/x(t-h) ]
				'index'	: reindex the series according to the parameter `base`
		n : int
			the period offset used in  the built-in method functions
		h : int
			forcing the number-of-periods-per-year value
		base : str | datetime-like
			if `method` is 'index', `base` is the base year/period from which
			the series will be reindexed
		args : positional arguments
			arguments to pass to callable `method`
		kwargs : keyword arguments
			keyword arguments to pass to callable `method`

		Returns
		-------
		pandas DataFrame
		"""

		try:
			# assume `method` is a user-provided function
			if args and kwargs:
				df = method(self.data, *args, **kwargs)
			elif args:
				df = method(self.data, *args)
			elif kwargs:
				df = method(self.data, **kwargs)
			else:
				df = method(self.data)

		except TypeError:
			# now assume `method` is a string identifier of registered functions
			if method == 'index':
				rix = ReIndexer(base)
				return rix(self.data)

			else:
				# one of the time-series functions
				try:
					modifier = series_mods[method]
				except KeyError:
					raise KeyError(
						f"{repr(method)} is an unrecognized modification"
					) from None

				if not h:
					h = periods_per_year(self.data)
				df = modifier(self.data, n, h)

		return df
