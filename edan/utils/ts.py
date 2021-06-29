"""
utility functions for working with the time series data
"""

from __future__ import annotations

import pandas as pd

from edan.core.base import BaseSeries, BaseComponent


def infer_freq(obj):
	"""
	infer the frequency string from a Series, pandas DataFrame or Series, or
	pandas Index. the description of pandas' Offset Aliases can be found here:
		https://pandas.pydata.org/pandas-docs/stable/
		user_guide/timeseries.html#offset-aliases

	the pandas.infer_freq() method returns the frequency string of the provided
	pandas DataFrame or Series, and the string is constructed based on the on
	the OffsetAlias desctiption above

	Parameters
	----------
	obj : Series | DataFrame | Series | Index
		the object that we will infer the frequency of

	Returns
	-------
	str
	"""

	try:
		# assume DataFrame or Series
		idx = obj.index
	except AttributeError:
		if isinstance(obj, BaseSeries):
			idx = obj.data.index
		elif isinstance(obj, BaseComponent):
			idx = obj.default_mtype.data.index
		else:
			# assume pandas index
			idx = obj

	try:
		full_guess = pd.infer_freq(idx)
	except:
		raise TypeError(
			f"Unable to interpret frequency of index of type {repr(type(obj).__name__)}"
		) from None

	if not full_guess:
		return None

	# strip off the anchored offset
	guess = full_guess.split('-')[0]
	guess_set = set(guess)

	if 'Q' in guess_set:
		return 'Q'
	elif 'M' in guess_set:
		if (guess == 'SM') or (guess == 'SMS'):
			# semi-month frequencies
			return None
		return 'M'
	elif ('A' in guess_set) or ('Y' in guess_set):
		return 'A'
	elif guess == 'W':
		return 'W'
	elif guess in {'B', 'C', 'D'}:
		return 'D'


def infer_freq_by_series(obj) -> Union[str, List[str]]:
	"""
	infer the frequency of a collection of data objects. works on iterables of
	Series, DataFrames, and Series (including iterables containing all three
	types of objects). if a DataFrame has columns that are of different frequencies
	(for example, PCE Services [monthly] in one column and BFI Equipment [quarterly]
	in another, those frequencies will be determined separately.)

	Parameters
	----------
	obj : Series | DataFrame | Series | Iterable[Series, DataFrame, Series]
		the object(s) whose frequency will be infered

	Returns
	-------
	str | List[str]
		if `obj` was a single pandas Series or Series, a string is returned.
		otherwise, a list of frequency strings is returned
	"""

	if isinstance(obj, pd.Series):
		"""
		remove NA values that may be leftover from merging `obj` with series of
		higher frequency. For example, `s1` is a Series of monthly frequency, `s2`
		is a Series of quarterly frequency, and `df` is the DataFrame formed from
		joining the two together. the index of `df[s2]` will still be of monthly
		frequency, though
		"""
		return infer_freq(obj.dropna())

	elif isinstance(obj, BaseSeries):
		# drop data for same reason as we do Series
		return infer_freq(obj.data.dropna())

	elif isinstance(obj, pd.DataFrame):
		return [infer_freq(obj[c].dropna()) for c in obj.columns]

	else:
		try:
			freqs = list()
			for o in obj:
				freqs.append(infer_freq_by_series(o))
			return freqs
		except TypeError:
			raise TypeError(
				f"Cannot infer frequency of type {repr(type(obj).__name__)}"
			) from None

_periods_per_year_dict = {'A': 1, 'Q': 4, 'M': 12, 'W': 52, 'D': 365}
def periods_per_year(obj):
	"""
	compute the number of times a period occurs per year, given a Series,
	or pandas DataFrame, Series, or Index. these values are hardcoded as
		'A': 1,
		'Q': 4,
		'M': 12,
		'W': 52,
		'D': 365

	Parameters
	----------
	obj: Series | DataFrame | Series | Index

	Returns
	-------
	int
	"""
	freq_str = infer_freq(obj)
	return _periods_per_year_dict[freq_str]
