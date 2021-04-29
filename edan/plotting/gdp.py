"""
module for plotting classes and methods of GDP component data
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


class GDPPlotAccessor(GenericPlotAccessor):

	def __init__(self, obj, *args, **kwargs):
		"""initialize Component obj"""
		self.obj = obj


	def __call__(
		self,
		gtype: str = 'level',
		method: Union[Callable, str, dict] = '',
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		subs: Union[bool, str, Iterable[str]] = True,
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
		gtype : str
			the GDP type of data to plot. `level` and `price` are the only
			accepted values for the moment. An AttributeError will be thrown
			if this Component (and all its subcomponents, if `subs` is True)
			does not have that `gdp`

		method : Callable | str | dict
			modification of the data before printing. recognized strings are
			described in docs for `edan.gdp.modifications.ModificationAccessor`.
			the same goes for callable `methed`.
				if `method` is a dict, the first value is the modification method,
			and the following values are the keyword arguments that will be passed
			to the underlying ModificationAccessor. for example,

				>>> gdp = edan.gdp.GDP
				>>> gdp.plot(gtype='level', method={'foo': 'diff', 'n'=2})

			or

				>>> gdp.plot(gtype='price', method={'bar': 'index', 'base'=2009})

			notice the key of the method doesn't matter. I'm not particularly
			fond of this implementation but I'm not sure how to get keywords to
			the ModificationAccessor without putting them all into the __call__
			definition. if the first value of dict `method` is a callable, the
			other (key, value) pairs are interpreted as keyword arguments for
			the user-defined callable

		start : str | bool | datetime-like, optional, ( = '' )
			left bound for truncating observations. if `start` = True, it's set
			to the first valid index of the plotting dataset

		end : str | bool | datetime-like, optional, ( = '' )
			right bound for truncating observation. if `end` = True, it's set
			to the last valid index of the plotting dataset

		periods : int | str, optional, ( = 0 )
			number of observations to plot. only accepted str value is 'all',
			in which case every period will be plotted, regardless of what
			values of `start` and `end` are provided

		subs : bool | Iterable[str], optional ( = True )
			the subcomponents to include in the plot. if True (default), all
			subcomponents, and the top-level component, are plotted. if False,
			just the top-level component are shown. if an iterable of
			subcomponent names, only those components (along with the top-level)
			are displayed. if a string, top-level and chosen subcomponent are
			shown

		names : str | list, optional ( = '' )
			specifying the names that appear in the axis legend. by default the
			components' `short_name` are used. labels for `gtype = 'level'` or
			`gtype = 'price'`, and any modifications to data will automatically
			be added in this case.
				if `names = 'codes'`, the series codes from FRED or AlphaVantage
			will be used.
				if `names` is a list, those will be the entries in the axis
			legend, with no changes of any kind.

		interp : str | dict, optional ( = 'linear' )
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

		objs = [self.obj]
		if iterable_not_string(subs):
			for _sub in subs:
				objs.append(self.obj[_sub])
		else:
			if isinstance(subs, str):
				objs.append(self.obj[subs])
			elif isinstance(subs, bool):
				if subs:
					for _sub in self.obj._subs:
						objs.append(_sub)
			else:
				raise TypeError("'subs' must be of type 'bool', 'str', or iter of 'str'")

		# pass the as-yet unaltered data to the manager
		self.mgr = PlotDataManager(objs)

		# selecting the GDP type of the component(s)
		self.mgr.select_containers(gtype)

		# get the list of GDPSeries and apply any data modifications
		gseries = self.mgr.containers
		mod_data = self._apply_modification(gseries, method)

		# merge list of series/dataframes together, and truncate
		self.mgr.merge_print_data(mod_data)
		df = self.mgr.truncate(start=start, end=end, periods=periods)

		# get names for the legend entries
		series_names = self.mgr.series_names(names, gtype, self.mod_str)
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
		modify the underlying data of the GDPSeries as specified by `method`
		prior to plotting.

		Parameters
		----------
		data : Iterable[CoreSeries]
			an iterable of GDPSeries that will eventually be plotted. these are
			assumed to be the same objects stored in the PlotDataManager's
			`containers` attribute

		method : Callable | str | dict
			specification of how to modify data. for now, all GDPSeries in `data`
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

			# return the pandas Series, not the GDPSeries
			try:
				return [s.data for s in data]
			except AttributeError:
				return data
