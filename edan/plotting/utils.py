"""
plotting utilities, mostly for common data operations
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.aggregates.series import Series
from edan.aggregates.components import Component

from edan.utils.ts import (
	infer_freq,
	infer_freq_by_series
)
from edan.utils.dtypes import iterable_not_string


def get_print_data(
	obj: Union[Component, Series, DataFrame],
	mtype : str = ''
):
	"""
	return the data held in an edan or pandas container.

	Parameters
	----------
	obj : Component | edan Series | pandas Series | pandas DataFrame
		the data container object. if a pandas Series or DataFrame, nothing
		if done & and the object is immediately returned. if a Component, then
		the edan Series' data corresponding to the Component's attribute `mtype`
		is returned. if an edan Series, return the underlying data
	mtype : str ( = '' )
		the attribute of the Component that stores the desired data. for example,
		`mtype` could be one of {'quantity', 'price', 'nominal', 'real'} if `obj`
		is a NIPAComponent. if `mtype` is not provided, the Component's default
		printing mtype is used

	Returns
	-------
	print_data : pandas Series or DataFrame
	"""
	if isinstance(obj, (pd.Series, pd.DataFrame)):
		return obj
	elif isinstance(obj, Series):
		return obj.data
	elif isinstance(obj, Component):
		if mtype:
			mtype_series = getattr(obj, mtype)
			return mtype_series.data

		mtype_series = getattr(obj, obj._default_mtype)
		return mtype_series.data

	raise TypeError(
		f"cannot interpret `obj` of type {type(obj).__name__}. must be one of "
		"Component, edan Series, pandas Series, or pandas DataFrame."
	)


def truncate(
	data: Union[Series, DataFrame],
	start: Union[str, bool, Timestamp],
	end: Union[str, bool, Timestamp],
	periods: Union[int, str]
):

	"""
	truncate a DatetimeIndex-ed/PeriodIndex-ed pandas Series or DataFrame. all
	three of the truncation parameters are optional in the so we do make some
	assumptions about their default values, in a case-by-case basis:

		1) [start not provided], [end not provided], [periods not provided]
			last observation printed is the final observation of dataset.
			number of periods printed is set according to default_periods:
				default_periods = {
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
			`date_range` method, from which we take cues for this method

		6) [periods == 'all']
			every observation is printed, regardless of the provided values
			of `start` and `end`

	Parameters
	----------
	data : pandas Series | pandas DataFrame
		data to truncate. if the index is not a DatetimeIndex or PeriodIndex,
		a TypeError is thrown
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
	default_periods = {
		'A': 12, 'Q': 20, 'M': 60, 'W': 260, 'D': 365*5
	}

	try:
		idx = data.index
		if not isinstance(idx, (pd.DatetimeIndex, pd.PeriodIndex)):
			raise TypeError(
				f"{repr(idx)}. data must have a DatetimeIndex or PeriodIndex "
				"to truncate"
			)
	except AttributeError:
		raise TypeError(
			f"{repr(data)}. data must have an `index` property in order to truncate"
		) from None

	if not periods:
		# if periods is 0, use the default value according to frequency
		freqstr = infer_freq(data)
		if freqstr:
			periods = default_periods[freqstr]
		else:
			# couldn't infer frequency for some reason, use the more general method
			freqs = infer_freq_by_series(df)

			# if series are of different frequencies, default to showing the
			#	number of periods of the highest freq
			periods_by_series = [default_periods[f] for f in freqs]
			periods = max(periods_by_series)

	elif isinstance(periods, str):
		# print all periods
		if periods.lower().strip() == 'all':
			return data
		else:
			raise ValueError("the only accepted str value of 'periods' is 'all'")

	if not start and not end:
		end = data.last_valid_index()
		return data.loc[:end].iloc[-periods:]

	if start and end:
		if isinstance(start, bool):
			start = data.first_valid_index()
		if isinstance(end, bool):
			end = data.last_valid_index()
		return data.loc[start:end]

	elif start:
		if isinstance(start, bool):
			start = data.first_valid_index()
		return data.loc[start:].iloc[:periods]

	elif end:
		if isinstance(end, bool):
			end = data.last_valid_index()
		return data.loc[:end].iloc[-periods:]

	raise ValueError(
		f"unable to interpret plotting dataset from 'start': {repr(start)}, "
		f"'end': {repr(end)}, 'periods': {repr(periods)}."
	)


def cumulate_data(df: pd.DataFrame):
	"""
	prepare data that will be plotted as stacked bars (or maybe areas) when
	some of the datapoints could be negative. this is necessary because plotting
	stacked bars/areas uses the `bottom` keyword, which allows us to set the lower
	bound of each bar precisely. we enforce a 0-neg bottom negative values and
	0+pos bottom to positive ones.

	https://stackoverflow.com/questions/35979852/stacked-bar-chart-using-
	python-matplotlib-for-positive-and-negative-values

	Parameters
	----------
	df : pandas DataFrame
		column-oriented data with possibly negative values

	Returns
	-------
	cumulated : pandas DataFrame
	"""

	# take negative & positive data apart and cumulate
	def get_cumulated_array(arr, **kwargs):
		cum = arr.clip(**kwargs)
		cum = np.cumsum(cum, axis=0)

		dat = np.zeros(np.shape(arr))
		dat[1:] = cum[:-1]
		return dat

	arr = df.values.transpose()
	cumulated_data = get_cumulated_array(arr, min=0)
	cumulated_data_neg = get_cumulated_array(arr, max=0)

	# re-merge positive & negative data
	row_mask = (arr < 0)
	cumulated_data[row_mask] = cumulated_data_neg[row_mask]

	return pd.DataFrame(
		cumulated_data.transpose(),
		index=df.index,
		columns=df.columns
	)


def collect_legend_entries(
	comp: Iterable[Component, Component] = None,
	method: Union[str, dict, Callable, Iterable] = None
):
	"""
	function for consistently ordering the legend entries of a plot.

	Parameters
	----------
	comp : Component | Iterable[Component] ( = None )
		the Components whose display names will be added to the legend
		entry. if an iterable, the display order is that of the iterable
	method : str | dict | Callable | Iterable[str, dict, Callable] ( = None )
		methods that have been used to transform the data. if `method` and
		`comp` are both provided, the ordering of the entries is: first Comp
		and all its methods, second Comp and all its methods, and so on

	Returns
	-------
	entries : list of legend entries
	"""

	if comp and method:

		def _fmt_method(m):
			if isinstance(m, str):
				return f'({m})'

			elif isinstance(m, dict):
				name = list(m.values())[0]
				return f'({name})'

			elif callable(m):
				return '(custom)'

			else:
				return '(trans.)'

		if iterable_not_string(method) and len(method) > 1:
			mentries = [_fmt_method(m) for m in method]
		else:
			# don't add method identifiers if only one
			try:
				return [c.display_name for c in comp]
			except TypeError:
				return c.display_name

		try:
			entries = []
			# assume list of components
			for c in comp:
				entries.extend([' '.join([c.display_name, m]) for m in mentries])
			return entries

		except TypeError:
			# Component is not iterable
			if mentries:
				return [f'{comp.display_name} {m}' for m in mentries]
			return comp.display_name

	elif comp:
		try:
			return [c.display_name for c in comp]
		except TypeError:
			# Component is not iterable
			return c.display_name

	raise ValueError(f"'comp': {comp} and 'method': {method}")
