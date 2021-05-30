"""
module for plotting classes and methods of NIPA component data
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from cycler import cycler

from edan.utils.dtypes import (
	iterable_not_string
)

from edan.plotting.generic import (
	GenericPlotAccessor,
	PlotDataManager
)
import edan.plotting.colors as colors


class ContributionPlot(object):
	"""
	create a chart where the subcomponents are stacked bars and the aggregate
	growth rate is a line
	"""
	def __init__(
		self,
		obj: Component,
		subs: Union[bool, str, Iterable[str]] = None,
		level: int = 0,
		method: Union[Callable, str, dict] = ''
	):
		self.obj = obj
		self.method = method

		# 'subs' is true by default in this method signature, so we shouldn't
		#	use the normal `self.obj.disaggregate(subs, level)`, in case 'level'
		#	is provided
		if level:
			df = self.obj.contributions(level=level, method=method)
			subcomponents = self.obj.disaggregate(level=level)
		else:
			df = self.obj.contributions(subs=subs, method=method)
			subcomponents = self.obj.disaggregate(subs=subs)

		# pass the aggregate & subcomponents to the manager. the `contributions`
		#	method above handles all the actual data stuff, but the manager will
		#	handle names
		objs = [self.obj] + list(subcomponents)
		self.mgr = PlotDataManager(objs)
		self.mgr.merge_print_data(df)

	def cumulate_data(self, data: pd.DataFrame):
		"""
		the bottom keyword in ax.bar or plt.bar allows us to set the lower bound
		of each bar precisely. Apply a 0-neg bottom to negative values, and 0-pos
		bottom to positive ones.

		https://stackoverflow.com/questions/35979852/stacked-bar-charts-using-
		python-matplotlib-for-positive-and-negative-values
		"""

		# take negative & positive data apart and cumulate
		def get_cumulated_array(arr, **kwargs):
			cum = arr.clip(**kwargs)
			cum = np.cumsum(cum, axis=0)

			dat = np.zeros(np.shape(arr))
			dat[1:] = cum[:-1]
			return dat

		arr = data.values.transpose()
		cumulated_data = get_cumulated_array(arr, min=0)
		cumulated_data_neg = get_cumulated_array(arr, max=0)

		# re-merge positive & negative data
		row_mask = (arr < 0)
		cumulated_data[row_mask] = cumulated_data_neg[row_mask]

		return pd.DataFrame(
			cumulated_data.transpose(),
			index=data.index,
			columns=data.columns
		)


	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		names: Union[str, list] = '',
		*args, **kwargs
	):

		# truncate data as requested
		df = self.mgr.truncate(start=start, end=end, periods=periods)

		# names for legend entries
		series_names = self.mgr.series_names(names, self.method)
		df.columns = series_names

		# create the axes that everything will be shown on
		ax = df.iloc[:, 0].plot(label=series_names[0])

		# after the main line has been plotted above, we don't want the contr
		#	bars to have that same color
		contr_colors = colors.contribution_palette()
		ax.set_prop_cycle(cycler('color', contr_colors))

		# matplotlib doesn't cumulate negative & positive bars natively, so
		#	we need to compute the `bottom` for each of the bars
		data_stack = self.cumulate_data(df.iloc[:, 1:])

		# pandas automatically interprets x-labels on bar charts as categories, so
		#	we have to directly interact with the axes. see this for more detail:
		# https://stackoverflow.com/questions/30133280/pandas-bar-plot-changes-date-format
		for i in range(1, df.shape[1]):
			ax.bar(
				df.index, df.iloc[:, i],
				bottom=data_stack.iloc[:, i-1], label=series_names[i]
			)
		ax.legend()

		return ax


class SharePlot(object):
	"""
	plot a stacked area chart of the shares attributable to each of the chosen
	subcomponents
	"""

	def __init__(
		self,
		obj: Component,
		subs: Union[bool, str, Iterable[str]] = True,
		level: int = 0,
		mtype: str = 'nominal'
	):
		self.obj = obj
		self.mtype = mtype

		# 'subs' is true by default in this method signature, so we shouldn't
		#	use the normal `self.obj.disaggregate(subs, level)`, in case 'level'
		#	is provided
		if level:
			df = self.obj.shares(level=level, mtype=mtype)
			subcomponents = self.obj.disaggregate(level=level)
		else:
			df = self.obj.shares(subs=subs, mtype=mtype)
			subcomponents = self.obj.disaggregate(subs=subs)

		# pass the subcomponents to the manager. the `shares` method above
		#	handles all the actual data stuff, but the manager will handle names
		self.mgr = PlotDataManager(subcomponents)

		# remove the first aggregate column b/c it's just a series of ones
		sub_data = df.iloc[:, 1:]
		self.mgr.merge_print_data(sub_data)

	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		names: Union[str, list] = '',
		*args, **kwargs
	):

		# truncate data as requested
		df = self.mgr.truncate(start=start, end=end, periods=periods)

		# names for legend entries
		series_names = self.mgr.series_names(names, self.mtype)
		df.columns = series_names

		return df.plot.area(*args, **kwargs)




class NIPAPlotAccessor(GenericPlotAccessor):

	def __init__(self, obj, *args, **kwargs):
		"""initialize Component obj"""
		self.obj = obj


	def __call__(
		self,
		mtype: str = '',
		method: Union[Callable, str, dict] = 'difa%',
		feature: str = '',
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		subs: Union[bool, str, Iterable[str]] = '',
		level: int = 0,
		names: Union[str, list] = '',
		interp: Union[str, dict] = 'linear',
		*args, **kwargs
	):
		"""
		primary plotting method for Component classes. in general the plotting
		methodology is handled entirely by the pandas.DataFrame.plot() method.
		the named keyword arguments in the function definition all apply to data
		selection / alteration prior to plotting

		Parameters
		----------
		mtype : str ( = 'real' )
			the GDP type of data to plot. accepted values are {'quantity', 'price',
			'nominal', and 'real'}. An AttributeError will be thrown if this
			Component (and all its subcomponents, if `subs` is True) does not have
			that `mtype`

		method : Callable | str | dict ( = 'difa%' )
			modification of the data before printing. recognized strings are
			described in docs for `edan.nipa.modifications.ModificationAccessor`.
			the same goes for callable `methed`.
				if `method` is a dict, the first value is the modification method,
			and the following values are the keyword arguments that will be passed
			to the underlying ModificationAccessor. for example,

				>>> gdp = edan.gdp.GDP
				>>> gdp.plot(mtype='real', method={'foo': 'diff', 'n'=2})

			or

				>>> gdp.plot(mtype='price', method={'bar': 'index', 'base'=2009})

			notice the key of the method doesn't matter. I'm not particularly
			fond of this implementation but I'm not sure how to get keywords to
			the ModificationAccessor without putting them all into the __call__
			definition.
				if the first value of dict `method` is a callable, the
			other (key, value) pairs are interpreted as keyword arguments for
			the user-defined callable.
				if no modification is desired, pass empty string or None

		feature : str ( = '' )
			the feature of the Component to plot. plotting schemes for each of the
			features are:
				'contributions' - the growth rate of the aggregate component is
					plotted as a line, and the contributions to growth of each of
					the subcomponents is part of a stacked bar. by default the
					growth rate is 'difa%', according to the Contribution Feature
					class, but alterations can be passed through the 'method'
					parameter here
				'shares' - the shares of each of the subcomponents are plotted
					as a stacked area chart, and the aggregate is not displayed.
					by default the mtype is 'nominal', according to the Share Feature
					class, but alterations can be passed through the 'mtype'
					parameter here

		start : str | bool | datetime-like ( = '' )
			left bound for truncating observations. if `start` = True, it's set
			to the first valid index of the plotting dataset

		end : str | bool | datetime-like ( = '' )
			right bound for truncating observation. if `end` = True, it's set
			to the last valid index of the plotting dataset

		periods : int | str ( = 0 )
			number of observations to plot. only accepted str value is 'all',
			in which case every period will be plotted, regardless of what
			values of `start` and `end` are provided

		subs : bool | Iterable[str] | str ( = True )
			the subcomponents to include in the plot. if True (default), all
			subcomponents, and the top-level component, are plotted. if False,
			just the top-level component is shown. if an iterable of subcomponent
			names, or single name, only those components (along with the top-
			level component) are displayed.

		level : int ( = 0 )
			the level, relative to the top-level Component, of subcomponents that
			are to be plotted.

		names : str | list ( = '' )
			specifying the names that appear in the axis legend. by default the
			components' `short_name` are used. labels for `mtype = 'real'` or
			other recognized mtypes, and any modifications to data will automatically
			be added in this case.
				if `names = 'codes'`, the series codes from FRED or AlphaVantage
			will be used.
				if `names` is a list, those will be the entries in the axis
			legend, with no changes of any kind.

		interp : str | dict ( = 'linear' )
			if a subset of the printing data is of a lower frequency than at
			least one other series, this parameter determines how the lower
			frequency data should be interpolated. this parameter is passed
			directly to the pandas.DataFrame.interpolate() method, which should
			be referred to if the full documentation is needed.
				much like the interpretation of the `method` parameter for this
			__call__ method, if a dictionary is passed, it is assumed the first
			value is the interpolation method, and any other (key, value) pairs
			are assumed to be keyword arguments for the pandas interpolate()
			method

		args : arguments
			positional arguments to pass to pandas.DataFrame.plot()

		kwargs : keyword arguments
			keyword arguments to pass to pandas.DataFrame.plot()


		Returns
		-------
		matplotlib AxesSubplot
		"""

		if feature:
			if feature == 'contributions':
				plotter = ContributionPlot(self.obj, subs, level, method)

			elif feature == 'shares':
				# we want default mtype for 'SharePlot' to be nominal, but the
				#	default mtype for other plots to be real, so we need `if`:
				mtype = mtype if mtype else 'nominal'
				plotter = SharePlot(self.obj, subs, level, mtype)

			else:
				raise ValueError(f"{repr(feature)} is unrecognized 'feature'")

			return plotter.plot(start, end, periods, names, *args, **kwargs)

		# 'subs' is true by default in this method signature, so we shouldn't
		#	use the normal `self.obj.disaggregate(subs, level)`, in case 'level'
		#	is provided
		if level:
			subcomponents = self.obj.disaggregate(level=level)
		else:
			subcomponents = self.obj.disaggregate(subs=subs)

		objs = [self.obj] + list(subcomponents)

		# pass the as-yet unaltered data to the manager
		self.mgr = PlotDataManager(objs)

		# selecting the GDP type of the component(s). different default mtypes
		#	for SharePlot & normal plot, hence the `if` below
		mtype = mtype if mtype else 'real'
		self.mgr.select_containers(mtype)

		# get the list of NIPASeries and apply any data modifications
		mseries = self.mgr.containers
		mod_data = self._apply_modification(mseries, method)

		# merge list of series/dataframes together, and truncate
		self.mgr.merge_print_data(mod_data)
		df = self.mgr.truncate(start=start, end=end, periods=periods)

		# get names for the legend entries
		series_names = self.mgr.series_names(names, mtype, self.mod_str)
		df.columns = series_names

		# interpolate, if need be
		df = self.manage_interpolation(df, method=interp)
		return df.plot(*args, **kwargs)


	def _apply_modification(
		self,
		data: Iterable[CoreSeries],
		method
	):
		"""
		modify the underlying data of the NIPASeries as specified by `method`
		prior to plotting.

		Parameters
		----------
		data : Iterable[CoreSeries]
			an iterable of NIPASeries that will eventually be plotted. these are
			assumed to be the same objects stored in the PlotDataManager's
			`containers` attribute

		method : Callable | str | dict
			specification of how to modify data. for now, all NIPASeries in `data`
			will have the same method applied to them. for documentation of how
			the different method types are interpreted, see __call__ method of
			GDPPlotAccessor. for documentation of the built-in recognized
			`method` string identifiers, see `edan.gdp.ModificationAccessor`

		Returns
		-------
		Iterable[pandas DataFrame]
		"""
		if method:
			try:
				# `method` is a dict
				keys = list(method.keys())
				mod_method = method.pop(keys[0])

				# saving the modification method string for labeling legend entries
				if isinstance(mod_method, str):
					self.mod_str = '(' + mod_method + ')'
					if mod_method == 'index':
						self.mod_str = '(index=' + str(method['base']) + ')'
				else:
					self.mod_str = '(custom mod)'
				return [s.modify(mod_method, **method) for s in data]

			except AttributeError:
				# `method` is string or Callable

				# saving the modification method string for labeling legend entries
				if isinstance(method, str):
					self.mod_str = '(' + method + ')'
				else:
					self.mod_str = '(custom mod)'
				return  [s.modify(method) for s in data]

		else:
			# no modification method
			self.mod_str = ''

			# return the pandas Series, not the NIPASeries
			try:
				return [s.data for s in data]
			except AttributeError:
				return data
