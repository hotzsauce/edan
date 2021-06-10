"""
module for functions of time series data of the Series containers, and for
Features of aggregate-able data. 'Features' are distinct from the 'transformations'
here because Features involve more than just a growth rate or moving average of
a single series - sometimes they even might involve data from other, related
aggregate components
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.aggregates.components import Component

from edan.utils.ts import (
	infer_freq,
	periods_per_year
)

from edan.utils.dtypes import iterable_not_string


class DataTransform(object):
	__slots__ = ['method', 'func', '_unit']
	def __init__(self, method, func, unit):
		self.method = method
		self.func = func
		self._unit = unit

	def fmt_unit(self, **kwargs):
		n, h, f = kwargs.get('n', 1), kwargs.get('h', 0), kwargs.get('freq', '')
		if n == 1 and h == 0:
			return self._unit
		elif n != 1:
			if f:
				return f"{n}-{f} {self._unit}"
			else:
				return f"{n}-prd. {self._unit}"
		return self._unit

	def __call__(self, data, n, h):
		return self.func(data, n, h)

series_transforms = dict()
def deft(key, func, unit=''):
	"""define transform"""
	series_transforms[key] = DataTransform(key, func, unit)

deft('diff',	lambda s, n, h: s.diff(n), 'chg.')
deft('diff%',	lambda s, n, h: 100 * (s.divide(s.shift(n)) - 1), '% chg.')
deft('diffl',	lambda s, n, h: 100 * np.log(s.divide(s.shift(n))), 'log chg.')
deft('difa',	lambda s, n, h: (h/n) * s.diff(n), 'ann. chg.')
deft('difa%',	lambda s, n, h: 100 * ( s.divide(s.shift(n)) ** (h/n) - 1), 'ann. % chg.')
deft('difal',	lambda s, n, h: 100 * (h/n) * np.log(s.divide(s.shift(n))), 'ann. log chg.')
deft('difv',	lambda s, n, h: s.diff(n)/n, 'avg. chg.')
deft('difv%',	lambda s, n, h: 100 * (s.divide(s.shift(n)) ** (h/n) - 1), 'avg. % chg.')
deft('difvl',	lambda s, n, h: (100/n) * np.log(s.divide(s.shift(n))), 'avg. log chg.')
deft('movv',	lambda s, n, h: s.rolling(n).mean(), 'moving avg.')
deft('mova',	lambda s, n, h: h * s.rolling(n).mean(), 'ann. moving avg.')
deft('movt',	lambda s, n, h: s.rolling(n).sum(), 'moving sum')
deft('yryr',	lambda s, n, h: s.diff(h), 'yr/yr chg.')
deft('yryr%',	lambda s, n, h: 100 * (s.divide(s.shift(h)) - 1), 'yr/yr % chg.')
deft('yryrl',	lambda s, n, h: 100 * np.log(s.divide(s.shift(h))), 'yr/yr log chg.')


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
			raise IndexError(f"no data in the year {self.base}")

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

		if rebase.empty:
			raise IndexError(f"no data in the rebase period {self.base}")

		return rebase


	@property
	def base_data(self):
		"""
		return the data that will be used to re-base the index
		"""
		if isinstance(self.base, int):
			return self.base_data_from_integer()
		return self.base_data_from_datetime()


	def __call__(self, data):

		self.data = data

		rebase = self.base_data
		base_value = rebase.mean(axis='index')

		return 100 * self.data / base_value


class TransformationAccessor(object):

	def __init__(self, obj, *args, **kwargs):
		if isinstance(obj, (pd.Series, pd.DataFrame)):
			self.data = obj
		else:
			self.data = obj.data

	def __call__(
		self,
		method: Union[str, Callable, Iterable[str, dict]] = 'difa%',
		n: int = 1,
		h: int = 0,
		base: Union[str, int, TimeStamp] = '',
		**kwargs
	):
		"""
		transform the data according to parameter `method`. a Series or DataFrame
		is returned depending on if `method` is a non-string, non-dict iterable
		or not. the column labels/Series name are set to the `method` strings.
		the 'n', 'h', and 'base' parameters must be passed as keywords

		throughout these comments/docs, the conventions are:
			x(t)	: observation of time series x at time t
			h		: the number of observations of x per year
			n		: the additional user-given parameter

		Parameters
		----------
		method : str | Callable | dict
			specification of how data will be transformed. recognized string values
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
							100 *[ x(t)/x(t-h) ] - 1
				'yryrl' : year-over-year log change
							100 * ln[ x(t)/x(t-h) ]
				'index'	: reindex the series according to the parameter `base`

			if a Callable, `self.data` will be passed as the first argument, with
			positional and keyword arguments passed if provided here. if dict,
			the first value is assumed to be the method name, and the other entries
			will be passed to `n`, `h`, `base`, or `kwargs`, as appropriate.
			for example,

				>>> gdp = edan.nipa.GDPTable['gdp']
				>>> gdp.transform(mtype='real', method={'foo': 'diff', 'n':2})

			or

				>>> gdp.transform(mtype='price', method={'bar': 'index', 'base':2009})

			the key of the method doesn't matter in terms of functionality - it
			doesn't affect the calculations - but it is used as the name of the
			column
				note: if any of the entries of the dict beyond the first have key
			values of `n`, `h`, or `base`, those are popped & passed to those
			arguments in the __transform__ signature, as opposed to going through the
			general **kwargs arg. the only consequence of this is that if the first
			entry of the dict is a callable, its keyword arguments should not be
			any of {`n`, `h`, `base`}
				if `method` is an iterable of the above, the same logic is
			applied to each entry

		n : int
			the period offset used in  the built-in method functions
		h : int
			forcing the number-of-periods-per-year value
		base : str | datetime-like
			if `method` is 'index', `base` is the base year/period from which
			the series will be reindexed
		kwargs : keyword arguments
			keyword arguments to pass to callable `method`

		Returns
		-------
		transform : pandas DataFrame or Series
		"""

		if isinstance(method, (str, dict)) or callable(method):
			return self.__transform__(method, n, h, base, **kwargs)

		elif iterable_not_string(method):

			frames = []
			for meth in method:
				df = self.__transform__(meth, n, h, base, **kwargs)
				frames.append(df)

			df = pd.concat(frames, axis='columns').dropna(axis='index', how='all')
			return df

		else:
			raise TypeError(method)

	def __transform__(self,
		method: Union[str, dict, Callable] = 'difa%',
		n: int = 1,
		h: int = 0,
		base: Union[str, TimeStamp] = '',
		**kwargs
	):

		try:
			# assume `method` is a dict
			keys = list(method.keys())

			method_copy = method.copy()
			first_key = keys[0]
			maybe_callable = method[first_key]

			if callable(maybe_callable):
				_ = method_copy.pop(first_key)
				kwargs.update(method_copy)
				df = self.__transform__(maybe_callable, **kwargs)

			else:
				n_ = method_copy.pop('n', n)
				h_ = method_copy.pop('h', h)
				base_ = method_copy.pop('base', base)
				df = self.__transform__(maybe_callable, n_, h_, base_)

		except AttributeError:
			# assume `method` is a user-provided function

			if callable(method):
				if kwargs:
					df = method(self.data, **kwargs)
				else:
					df = method(self.data)

			else:
				# now assume `method` is a string identifier of registered functions
				if method == 'index':
					rix = ReIndexer(base)
					return rix(self.data)

				else:
					# one of the time-series functions
					try:
						transformer = series_transforms[method]
					except KeyError:
						raise KeyError(
							f"{repr(method)} is an unrecognized transformation"
						) from None

					if not h:
						h = periods_per_year(self.data)
					df = transformer(self.data, n, h)

		return df


def transform(
	obj: Union[Component, Series, DataFrame],
	method: Union[str, Iterable[str]] = '',
	n: int = 1,
	h: int = 0,
	base: Union[int, str] = '',
	mtype: str = '',
	**kwargs
):
	"""
	top-level function for built-in transforms. parameters are the same as those
	in the `__call__` method of the TransformationAccessor
	"""
	if isinstance(obj, Component):
		if mtype:
			series = obj.__getattr__(mtype)
		else:
			series = obj.default_mtype
		transformer = TransformationAccessor(series)
		return transformer(method, n, h, base, **kwargs)

	transformer = TransformationAccessor(obj)
	return transformer(method, n, h, base, **kwargs)


class Feature(object):
	"""
	Features are intended to be CachedAccessors of Components, or used via the
	methods of the same name that are defined elsewhere in that concept's module
	"""

	name = ''

	def compute(self, *args, **kwargs):
		"""this should be overriden by subclasses"""
		feat = type(self).__name__
		raise NotImplementedError(f"'compute' method not defined for {feat} feature")

	def __init__(self, obj=None, *args, **kwargs):
		self.obj = obj

	def __call__(self, *args, **kwargs):
		"""
		when called as a method of a Component, i.e.

			>>> gdp = edan.nipa.GDPTable['gdp']
			>>> gdp.{feature}()

		the subclass' `compute` method is called and returned
		"""
		return self.compute(*args, **kwargs)
