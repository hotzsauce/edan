"""
classes for plotting Features of Components in particular ways
"""

from __future__ import annotations

import edan.plotting as plt
import edan.plotting.colors as colors
from edan.plotting.utils import (
	cumulate_data,
	truncate,
	collect_legend_entries
)


class ContributionPlotter(object):
	"""
	create a chart where the subcomponents are stacked bars and the
	aggregate growth rate is a line
	"""

	def __init__(
		self,
		comp: Component,
		subs: Union[bool, str, Iterable[str]] = '',
		level: int = 0,
		method: str = 'difa%',
		**kwargs
	):
		self.comp = comp
		self.method = method if method else 'difa%'

		self.subcomponents = self.comp.disaggregate(subs=subs, level=level)
		self.data = self.comp.contributions(subs=subs, level=level, method=self.method)

	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0
	):
		self.data = truncate(self.data, start, end, periods)

		# for some very odd reason, if there was a figure created before this
		#	Plotter was created, the Contributions plot is drawn on the previous
		#	figure. this doesn't happen with the SharesPlot, or the general
		#	ComponentPlotter. create a dummy figure and axes as a buffer
		_, _ = plt.subplots()

		# plot the aggregate component as a line
		ax = self.data.iloc[:, 0].plot()

		# after the main line has been plotted, remove the aggregate color
		palette = colors.color_palette()
		ax.set_prop_cycle(palette.contribution_cycler())

		# plot each of the component bars, stacked
		data_stack = cumulate_data(self.data.iloc[:, 1:])
		for i in range(1, self.data.shape[1]):
			ax.bar(
				self.data.index,
				self.data.iloc[:, i].values,
				bottom=data_stack.iloc[:, i-1].values
			)

		return ax

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
		subs: Union[bool, str, Iterable[str]] = '',
		level: int = 0,
		mtype: str = '',
		**kwargs
	):
		self.comp = comp
		self.mtype = mtype if mtype else 'nominal'

		self.subcomponents = self.comp.disaggregate(subs=subs, level=level)

		# remove the first column - the aggregate columns of ones
		data = self.comp.shares(subs=subs, level=level, mtype=self.mtype)
		self.data = data.iloc[:, 1:]

	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0
	):
		self.data = truncate(self.data, start, end, periods)

		return self.data.plot.area(stacked=True)

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
