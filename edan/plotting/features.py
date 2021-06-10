"""
classes for plotting Features of Components in particular ways
"""

from __future__ import annotations

from cycler import cycler

from edan.plotting.utils import (
	cumulate_data,
	truncate,
	collect_legend_entries
)
import edan.plotting.colors as colors



class ContributionPlotter(object):
	"""
	create a chart where the subcomponents are stacked bars and the
	aggregate growth rate is a line
	"""

	def __init__(
		self,
		comp: Component,
		canvas: EdanCanvas,
		method: str = 'difa%',
		start: Union[str, bool, TimeStamp] = '',
		end: Union[str, bool, TimeStamp] = '',
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

		self.method = method

		self.start = start
		self.end = end
		self.periods = periods

		self.subcomponents = self.comp.disaggregate(subs=subs, level=level)
		self.data = self.comp.contributions(subs=subs, level=level, method=method)

	def plot(self):
		self.data = truncate(self.data, self.start, self.end, self.periods)

		# plot the aggregate component as a line. use pandas' PlotAccessor to
		#	set the widths of the bars
		self.data.iloc[:, 0].plot(ax=self.ax)

		# after the main line has been plotted, remove the aggregate color
		contr_colors = colors.contribution_palette()
		self.ax.set_prop_cycle(cycler('color', contr_colors))

		# matplotlib doesn't cumulate negative & positive bars natively, so
		#	the bottom for each of the bars is computed here
		data_stack = cumulate_data(self.data.iloc[:, 1:])

		for i in range(1, self.data.shape[1]):
			self.ax.bar(
				self.data.index, self.data.iloc[:, i],
				bottom=data_stack.iloc[:, i-1],
			)

		self.canvas._arrange()
		return self.ax

	@property
	def title(self):
		return f"Contributions to growth of {self.comp.long_name.lower()}"

	@property
	def entries(self):
		if hasattr(self, '_entries'):
			return self._entries

		objs = [self.comp] + list(self.subcomponents)
		self._entries = collect_legend_entries(comp=objs)
		return self._entries

	@property
	def unit(self):
		return '% contr.'



class SharePlotter(object):
	"""
	plot a stacked area chart of the shares attributable to each of the chosen
	subcomponents
	"""

	def __init__(
		self,
		comp: Component,
		canvas: EdanCanvas,
		mtype: str = 'nominal',
		start: Union[str, bool, TimeStamp] = '',
		end: Union[str, bool, TimeStamp] = '',
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

		self.start = start
		self.end = end
		self.periods = periods

		if mtype:
			self.mtype = mtype
		else:
			self.mtype = self.comp._default_mtype

		self.subcomponents = self.comp.disaggregate(subs=subs, level=level)

		# remove first column (the aggregate component)
		data = self.comp.shares(subs=subs, level=level, mtype=self.mtype)
		self.data = data.iloc[:, 1:]

	def plot(self):
		self.data = truncate(self.data, self.start, self.end, self.periods)
		self.ax.stackplot(
			self.data.index,
			self.data.values.transpose()
		)
		self.canvas._arrange()
		return self.ax

	@property
	def title(self):
		mtype = self.mtype.capitalize()
		return ' '.join([mtype, 'shares of', self.comp.long_name.lower()])

	@property
	def entries(self):
		if hasattr(self, '_entries'):
			return self._entries

		self._entries = collect_legend_entries(comp=self.subcomponents)
		return self._entries

	@property
	def unit(self):
		return 'shares'


feature_maps = {
	'contributions': ContributionPlotter,
	'shares': SharePlotter
}
def get_feature(feat: str):
	"""
	retrieve a Feature plotter by Feature name

	Parameters
	----------
	feat : str
		the Feature name

	Returns
	-------
	Feature plotter
	"""
	try:
		return feature_maps[feat]
	except KeyError:
		raise KeyError(f"{repr(feat)} is an unrecognized Feature plotter") from None
