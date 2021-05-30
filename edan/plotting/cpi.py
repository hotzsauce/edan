"""
module for plotting classes and methods of CPI component data
"""

from __future__ import annotations

import pandas as pd

from edan.utils.dtypes import (
	iterable_not_string
)

from edan.plotting.generic import (
	GenericPlotAccessor,
	PlotDataManager
)



class CPIPlotAccessor(GenericPlotAccessor):

	def __init__(self, obj, *args, **kwargs):
		"""initialize Component obj"""
		self.obj = obj


	def __call__(
		self,
		mtype: str = 'price',
		method: Union[Callable, str, dict] = 'difa%',
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
		mtype : str ( = 'price' )
			the GDP type of data to plot. 'price' is only accepted value for CPI
			data.

		method : Callable | str | dict ( = 'difa%' )
			transformation of the data before printing. recognized strings are
			described in docs for `edan.nipa.transformation.TransformationAccessor`.
			the same goes for callable `methed`.
				if `method` is a dict, the first value is the transformation method,
			and the following values are the keyword arguments that will be passed
			to the underlying TransformationAccessor. for example,

				>>> gdp = edan.gdp.GDP
				>>> gdp.plot(mtype='real', method={'foo': 'diff', 'n'=2})

			or

				>>> gdp.plot(mtype='price', method={'bar': 'index', 'base'=2009})

			notice the key of the method doesn't matter. I'm not particularly
			fond of this implementation but I'm not sure how to get keywords to
			the TransformationAccessor without putting them all into the __call__
			definition.
				if the first value of dict `method` is a callable, the
			other (key, value) pairs are interpreted as keyword arguments for
			the user-defined callable.
				if no transformation is desired, pass empty string or None

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
			other recognized mtypes, and any transforms to data will automatically
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

		# selecting the GDP type of the component(s)
		self.mgr.select_containers(mtype)

		# get the list of NIPASeries and apply any data transformations
		mseries = self.mgr.containers
		trans_data = self._apply_transformation(mseries, method)

		# merge list of series/dataframes together, and truncate
		self.mgr.merge_print_data(trans_data)
		df = self.mgr.truncate(start=start, end=end, periods=periods)

		# get names for the legend entries
		series_names = self.mgr.series_names(names, mtype, self.trans_str)
		df.columns = series_names

		# interpolate, if need be
		df = self.manage_interpolation(df, method=interp)
		return df.plot(*args, **kwargs)


	def _apply_transformation(
		self,
		data: Iterable[CoreSeries],
		method
	):
		"""
		transform the underlying data of the NIPASeries as specified by `method`
		prior to plotting.

		Parameters
		----------
		data : Iterable[CoreSeries]
			an iterable of NIPASeries that will eventually be plotted. these are
			assumed to be the same objects stored in the PlotDataManager's
			`containers` attribute

		method : Callable | str | dict
			specification of how to transform data. for now, all NIPASeries in `data`
			will have the same method applied to them. for documentation of how
			the different method types are interpreted, see __call__ method of
			GDPPlotAccessor. for documentation of the built-in recognized
			`method` string identifiers, see `edan.aggregates.transformations`

		Returns
		-------
		Iterable[pandas DataFrame]
		"""
		if method:
			try:
				# `method` is a dict
				keys = list(method.keys())
				trans_method = method.pop(keys[0])

				# saving the transformation method string for labeling legend entries
				if isinstance(trans_method, str):
					self.trans_str = '(' + trans_method + ')'
					if trans_method == 'index':
						self.trans_str = '(index=' + str(method['base']) + ')'
				else:
					self.trans_str = '(custom trans)'
				return [s.transform(trans_method, **method) for s in data]

			except AttributeError:
				# `method` is string or Callable

				# saving the transformation method string for labeling legend entries
				if isinstance(method, str):
					self.trans_str = '(' + method + ')'
				else:
					self.trans_str = '(custom trans)'
				return  [s.transform(method) for s in data]

		else:
			# no transformation method
			self.trans_str = ''

			# return the pandas Series, not the NIPASeries
			try:
				return [s.data for s in data]
			except AttributeError:
				return data
