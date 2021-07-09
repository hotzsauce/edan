"""
plotting core objects - Components & Series
"""
from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt

from edan.errors import FeatureError

from edan.utils.dtypes import iterable_not_string

from edan.plotting.generic import (
	plot_on_canvas,
	BasePlotter
)
from edan.plotting.features import get_feature
from edan.plotting.utils import (
	get_print_data,
	truncate,
	collect_legend_entries,
	apply_transformations
)
import edan.plotting.colors as colors



class ComponentPlotAccessor(object):

	def __init__(self, obj):
		self.obj = obj

	def __call__(
		self,
		subs: Union[bool, str, Iterable[str]] = True,
		level: int = 0,
		mtype: str = '',
		method: Union[Callable, str, dict] = '',
		feature: str = '',
		**kwargs
	):
		# by default we want to include the subcomponents on any time series
		#	plot with a Component, which is why `subs` default is `True`. in
		#	the usual `obj.disaggregate(subs, level)`, value of `subs` is checked
		#	first, so if `level` is provided here we overwrite the `subs` default
		if level:
			subs, level = '', level
		else:
			subs, level = subs, 0

		# Feature plotters have pre-configured plotting schemes
		if feature:
			if not isinstance(feature, str):
				raise TypeError("'feature' must be a string")

			if not hasattr(self.obj, feature):
				raise FeatureError(feature, self.obj)

			plotter_obj = get_feature(feature)

		else:
			plotter_obj = ComponentPlotter

		# instantiate plotter object here, then pass to generic method for shared
		#	steps
		plotter = plotter_obj(
			comp=self.obj,
			subs=subs,
			level=level,
			mtype=mtype,
			method=method
		)

		return plot_on_canvas(plotter, **kwargs)



# maps from frequency format codes to abbreviated frequency names
freq_abbrevs = {
	'A': 'ann.',
	'Q': 'qtr.',
	'M': 'mo.',
	'W': 'wkly.',
	'D': 'daily'
}
class ComponentPlotter(BasePlotter):
	"""
	class to retrieve, select, and transform data of components & its
	subcomponents before displaying
	"""

	def __init__(
		self,
		comp: Component,
		subs: Union[bool, str, Iterable[str]] = '',
		level: int = 0,
		mtype: str = '',
		method: Union[Callable, str, dict] = ''
	):
		self.comp = comp
		self.method = method

		if mtype:
			self.mtype = mtype
		else:
			self.mtype = self.comp._default_mtype

		self.subcomponents = self.comp.disaggregate(subs=subs, level=level)


	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0
	):
		self._collect_data()

		if self.method:
			self.data = apply_transformations(self.data, self.method)

		self.data = truncate(self.data, start, end, periods)

		# pandas plots consecutive `comp.plot()` calls on the same axes? this
		#	doesn't happen with features though
		fig, ax = plt.subplots()

		# if more than one series is plotted, and more than one transforms are
		#	being computed, use sequential colors
		if self.n_methods > 1:
			if self.data.shape[1] == self.n_methods:
				return self.data.plot(ax=ax)
			else:
				# use current palette to set sequential colors
				palette = colors.color_palette()
				ax.set_prop_cycle(palette.sequential_cycler(self.n_methods))

				return self.data.plot(ax=ax)

		return self.data.plot(ax=ax)

	def _collect_data(self):
		"""
		based on `subs` and `level` attributes, select the subcomponents that
		will be plotted alongside the aggregate component
		"""

		if self.subcomponents:
			objs = [self.comp] + list(self.subcomponents)
			frames = []

			for comp in objs:
				data = get_print_data(comp, self.mtype)
				data.name = comp.code
				frames.append(data)

			self.data = pd.concat(frames, axis='columns').dropna(how='all')

		else:
			self.data = get_print_data(self.comp, self.mtype)
			self.data.name = self.comp.code

	@property
	def title(self):
		if self.mtype:
			mtype = self.mtype.capitalize()
		else:
			mtype = self.comp._default_mtype.capitalize()
		return ' '.join([mtype, self.comp.long_name.lower()])

	@property
	def entries(self):
		if hasattr(self, '_entries'):
			return self._entries

		objs = [self.comp] + list(self.subcomponents)
		self._entries = collect_legend_entries(
			comp=objs,
			method=self.method
		)
		return self._entries

	@property
	def n_legend_cols(self):
		"""number of columns is determined by number of series & transforms"""
		if isinstance(self.data, pd.DataFrame):
			# if no methods, each data series will have their own legend col
			nm = self.n_methods
			if nm == 0:
				return self.data.shape[1]

			# if all the series are just different methods of a single time series,
			#	the legend entries will all be in a single row
			if nm == self.data.shape[1]:
				return nm
			return self.data.shape[1] // nm

		elif isinstance(self.data, pd.Series):
			return 1

		raise TypeError("data must be a pandas Series or DataFrame")

	@property
	def n_methods(self):
		"""the number of transformations applied to the plotting data"""
		if iterable_not_string(self.method):
			return len(self.method)

		elif isinstance(self.method, str):
			if self.method == '':
				return 0
			return 1


class SeriesPlotter(object):
	pass
