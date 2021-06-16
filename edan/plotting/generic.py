
from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt

from edan.aggregates.base import (
	BaseSeries,
	BaseComponent
)
from edan.aggregates.transformations import series_transforms

from edan.errors import FeatureError

from edan.utils.ts import infer_freq
from edan.utils.dtypes import iterable_not_string

from edan.plotting.features import get_feature

from edan.plotting.utils import (
	get_print_data,
	truncate,
	collect_legend_entries,
	apply_transformations
)

import edan.plotting.colors as colors



class PlotAccessor(object):

	def __init__(self, obj):
		self.obj = obj

	def __call__(self, **kwargs):
		return plot(self.obj, **kwargs)



def plot(
	obj: Union[Component, Series, DataFrame],
	subs: Union[bool, str, Iterable[str]] = True,
	level: int = 0,
	mtype: str = '',
	method: Union[Callable, str, dict] = '',
	feature: str = '',
	start: Union[str, bool, Timestamp] = '',
	end: Union[str, bool, Timestamp] = '',
	periods: Union[int, str] = 0,
	# EdanCanvas keywords
	ax: Axes = None,
	fig: Figure = None,
	figsize: tuple = (13, 8),
	title: str = '',
	subtitle: str = '',
	unit: str = '',
	legend: Union[bool, str, Iterable[str]] = True,
	**kwargs
):
	"""
	central plotting method
	"""
	if isinstance(obj, (BaseSeries, pd.Series, pd.DataFrame)):
		raise NotImplementedError(f"cannot plot {type(obj).__name__} yet")

	if isinstance(obj, BaseComponent):

		# by default we want to include the subcomponents on any time series
		#	plot with a Component, which is why `subs` default is `True`. in
		#	the usual `obj.disaggregate(subs, level)`, value of `subs` is checked
		#	first, so if level is provided here we overwrite the `subs` default
		if level:
			subs, level = '', level
		else:
			subs, level = subs, 0

		# feature plotters have pre-configured plotting schemes
		if feature:
			if not isinstance(feature, str):
				raise TypeError("'feature' must be a string")

			if not hasattr(obj, feature):
				raise FeatureError(feature, obj)

			plotter_obj = get_feature(feature)

		else:
			plotter_obj = ComponentPlotter

		plotter = plotter_obj(
			comp=obj,
			subs=subs,
			level=level,
			mtype=mtype,
			method=method
		)

		ax = plotter.plot(start, end, periods)
		fig = plt.gcf()

		canvas = EdanCanvas(
			plotter,
			ax,
			fig,
			figsize=figsize,
			title=title,
			subtitle=subtitle,
			unit=unit,
			legend=legend,
			**kwargs
		)
		canvas._arrange()

		return ax



class ComponentPlotter(object):
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

	@property
	def unit(self):
		if self.method:
			if isinstance(self.method, str):
				data_transform = series_transforms[self.method]
				return data_transform.fmt_unit()

			elif isinstance(self.method, dict):
				name = list(self.method.values())[0]

				try:
					data_transform = series_transforms[name]
					params = {k: v for k, v in self.method.items() if v != name}

					freq = infer_freq(self.data)
					abbrev = freq_abbrevs[freq]
					params['freq'] = abbrev

					return data_transform.fmt_unit(**params)

				except KeyError:
					# name was callable
					return self.method.get('unit', '')

			else:
				# self.method was callable
				return ''
		else:
			return 'level'


# maps from frequency format codes to abbreviated frequency names
freq_abbrevs = {
	'A': 'ann.',
	'Q': 'qtr.',
	'M': 'mo.',
	'W': 'wkly.',
	'D': 'daily'
}

class EdanCanvas(object):
	"""
	class that manages the placement of titles, subtitles, legends, and plotting
	areas of a figure
	"""

	# x- & y-location of title, subtitle, and unit label in fig.transFigure units
	_title_x = _subtitle_x = _unit_x = 0.05
	_title_y = 0.98		# this is also matplotlib's default for y-loc of suptitle
	_subtitle_y = 0.92
	_unit_y = 0.885

	def __init__(
		self,
		plotter,
		ax: Axes,
		fig: Figure,
		figsize: tuple = None,
		title: str = '',
		subtitle: str = '',
		unit: str = '',
		legend: Union[bool, str, Iterable[str]] = True,
		**kwargs
	):
		self.plotter = plotter
		self.ax, self.fig = ax, fig

		self.figsize = (13, 8) if figsize is None else figsize
		self.fig.set_size_inches(self.figsize)

		self.title = title
		self.subtitle = subtitle

		self.unit = unit
		self.legend = legend
		self.kwargs = kwargs

	def _arrange(self):
		self._add_title()
		self._add_subtitle()
		self._add_legend()
		self._add_unit_label()

	def _add_title(self):

		ha = self.kwargs.pop('title_loc', 'left')

		if ha == 'left':
			x, y = self._title_x, self._title_y
		elif ha == 'right':
			x, y = 1-self._title_x, self._title_y
		else:
			# matplotlib's default x-loc
			x, y = 0.5, self._title_y

		# if 'title' was provided, use that. otherwise, default to the plotter's
		if self.title:
			fig_title = self.title
		else:
			fig_title = self.plotter.title

		self.fig.suptitle(
			fig_title,
			x=x, y=y,
			horizontalalignment=ha,
			fontsize=16,
			fontweight='bold'
		)

	def _add_legend(self):

		if isinstance(self.legend, bool):
			if self.legend:
				display_names = self.plotter.entries
				self._arrange_legend(display_names)

		elif isinstance(self.legend, str):
			if self.legend == 'codes':
				# when creating the data, the plotter should have overwritten
				#	the column names with edan codes
				codes = self.plotter.data.columns
				self._arrange_legend(codes)
			else:
				raise ValueError("the only recognized str value of legend is 'codes'")

		else:
			raise TypeError(f"'legend' can only be bool or str right now")

	def _arrange_legend(self, entries):
		"""
		move the legend from the default matplotlib position to the top, where it
		spans the width of the axes
		"""

		# assume the plotter has arranged the entries - if not, draw them
		#	all in a single row
		try:
			ncols = self.plotter.n_legend_cols
		except AttributeError:
			ncols = len(self.plotter.entries)

		# number of series in the plotter's data
		try:
			_, ns = self.plotter.data.shape
		except ValueError:
			# self.plotter.data is pandas Series
			ns = 1

		nrows = ns // ncols

		# scaling factor is determined by number of rows
		if nrows > 2:
			scale = 0.90 - 0.05*(nrows - 2)
		else:
			scale = 0.90

		# shrink axis vertically according to number of legend rows
		box = self.ax.get_position()
		self.ax.set_position([box.x0, box.y0, box.width, box.height*scale])

		# need the figure scale so we can left-align left side of legend with title
		trans = self.fig.transFigure
		x, y = self._unit_x, box.y0 + scale*box.height

		# put a legend above current axis
		self.ax.legend(
			labels=entries,
			bbox_to_anchor=(x, y, x + box.width, 0.06),
			bbox_transform=trans,
			ncol=ncols,
			mode='expand',
			borderaxespad=0,
			frameon=False,
		)

	def _add_subtitle(self):
		"""
		the parameter 'subtitle' is displayed below the bold, larger fontsize
		'title', but because matplotlib bounds an axes title on the left and
		right by the axes borders, the `ax.set_title` method cannot be used to
		set the subtitle. instead, we have to use an onnotation box
		"""

		ha = self.kwargs.pop('subtitle_loc', 'left')

		if self.subtitle:
			# in orderto scale properly wwhen figure window changes side, plot
			#	on the Figure's transform
			trans = self.fig.transFigure

			# vertical loc of subtitle is just below figure title. this might
			#	cause problems if the title takes up more than one line
			y = 0.92
			if ha == 'left':
				# flush with title when title loc is 'left'
				x = 0.05
			elif ha == 'center':
				x = 0.5
			elif ha == 'right':
				# flush with title when title loc is 'right'
				x = 0.95
			else:
				if isinstance(ha, str):
					v = ('left', 'center', 'right')
					raise ValueError(f"'subtitle_loc' must be one of {' '.join(v)}")
				else:
					raise TypeError("'subtitle_loc' must be a str")

			self.ax.annotate(
				self.subtitle,
				(x, y), xycoords=trans,
				fontsize=12,
				ha=ha
			)

	def _add_unit_label(self):

		if self.unit:
			unit = self.unit
		else:
			unit = self.plotter.unit

		self.ax.annotate(
			unit,
			(self._unit_x, self._unit_y), xycoords=self.fig.transFigure,
			ha='left',
			fontsize=10
		)
