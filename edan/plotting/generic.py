"""
generic plotting classes shared across the different plot accessors
"""

from __future__ import annotations
from copy import deepcopy

import pandas as pd
# import matplotlib.pyplot as plt
import edan.plotting._matplotlib as plt

from edan.aggregates.transformations import (
	transform,
	series_transforms
)

from edan.plotting.features import get_feature
from edan.plotting.utils import (
	get_print_data,
	truncate,
	collect_legend_entries
)

from edan.utils.ts import infer_freq
from edan.utils.dtypes import iterable_not_string


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
		ax: Axes = None,
		fig: Figure = None,
		figsize: tuple = (13, 8),
		title: str = '',
		subtitle: str = '',
		unit: str = '',
		legend: Union[bool, str, Iterable[str]] = True,
		**kwargs
	):

		# setup axes and figure for both canvas & paired plotter
		if (ax is None) and (fig is None):
			self.fig, self.ax = plt.subplots()
		elif ax is None:
			self.fig, self.ax = fig, fig.gca()
		elif fig is None:
			self.fig, self.ax = plt.gcf(), ax
		else:
			self.fig, self.ax = fig, ax

		self.figsize = (13, 8) if figsize is None else figsize
		self.fig.set_size_inches(self.figsize)

		self.title = title
		self.subtitle = subtitle

		self.unit = unit
		self.legend = legend
		self.kwargs = kwargs

	def _pair_plotter(self, plotter):
		self.plotter = plotter

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

		# shrink axis vertically by 10%
		box = self.ax.get_position()
		self.ax.set_position([box.x0, box.y0, box.width, box.height*0.90])

		# need the figure scale so we can left-align left side of legend with title
		trans = self.fig.transFigure
		x, y = self._unit_x, box.y0 + 0.90*box.height

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


class ComponentPlotAccessor(object):

	def __init__(self, comp: Component):
		self.comp = comp

	def __call__(self, **kwargs):
		canvas = EdanCanvas(**kwargs)

		# by default we want to plot the subcomponents on any time series plots
		#	so we shouldn't use the normal `self.obj.disaggregate(subs, level)`
		#	in case `level` is provided
		subs, level = kwargs.pop('subs', ''), kwargs.pop('level', 0)
		if level:
			kwargs['subs'] = ''
			kwargs['level'] = level
		else:
			kwargs['subs'] = subs
			kwargs['level'] = 0

		feature = kwargs.pop('feature', '')
		if feature:
			fplotter = get_feature(feature)
			plotter = fplotter(self.comp, canvas, **kwargs)
			return plotter.plot()

		plotter = ComponentPlotter(self.comp, canvas, **kwargs)
		return plotter.plot()



class ComponentPlotter(object):
	"""
	class to retrieve, select, and transform data of components & its subcomponents
	before displaying. can be used as an accessor of a Component class via the
	__call__ methord
	"""

	def __init__(
		self,
		comp: Component,
		canvas: EdanCanvas,
		mtype: str = '',
		method: Union[Callable, str, dict] = '',
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		subs: Union[bool, str, Iterable[str]] = '',
		level: int = 0,
		**kwargs
	):
		self.comp = comp
		self.canvas = canvas
		self.canvas._pair_plotter(self)

		self.ax = self.canvas.ax
		self.fig = self.canvas.fig

		self.kwargs = kwargs

		self.mtype = mtype
		self.method = method

		self.start = start
		self.end = end
		self.periods = periods

		self.subcomponents = self.comp.disaggregate(subs, level)

	def plot(self):
		self._collect_data()
		self._apply_transformations()

		self.data = truncate(self.data, self.start, self.end, self.periods)

		self.ax.plot(
			self.data.index,
			self.data.values,
			label=self.entries
		)
		self.canvas._arrange()
		return self.ax

	def _collect_data(self):
		"""
		based on `subs` and `level` attributes, select the subcomponents that
		will be plotted alongside the aggregate component. the legend entrie
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

	def _apply_transformations(self):
		"""
		after `data` attribute has been set with _collect_print_data, apply the
		transform if provided, overwriting `self.data` in the process. if more
		than one method is provided, the columns will need to be reordered. this
		is because the `transform` method performs the operation on the block
		for each transform, than concats the blocks. on the other hand, the legend
		entries are ordered
			comp 1 (method 1), comp 1 (method 2), ..., comp 1 (method n),
				...					...						...
			comp m (method 1), comp m (method 2), ..., comp m (method n)
		"""
		if self.method:
			self.data = transform(self.data, self.method)

			if iterable_not_string(self.method) and len(self.method) > 1:

				nm = len(self.method)
				ns = self.data.shape[1] // nm

				idx = [i + nm*j for i in range(nm) for j in range(ns)]
				self.data = self.data.iloc[:, idx]

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
		# number of columns is determined by number of series & transforms
		nm = len(self.method) if iterable_not_string(self.method) else 1
		return self.data.shape[1] // nm

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
				# self.method was a callable
				return ''

		else:
			return 'level'
