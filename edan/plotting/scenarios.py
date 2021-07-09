
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from edan.plotting.generic import (
	plot_on_canvas,
	BasePlotter
)
from edan.plotting.utils import (
	get_print_data,
	truncate,
	apply_transformations
)
import edan.plotting.colors as colors



class ForecastPlotAccessor(object):

	def __init__(self, obj):
		self.obj = obj

	def __call__(
		self,
		method: Union[Callable, str, dict] = '',
		**kwargs
	):
		plotter = ForecastPlotter(self.obj, method)
		return plot_on_canvas(plotter, **kwargs)


# maps from frequency format codes to abbreviated frequency names
freq_abbrevs = {
	'A': 'ann.',
	'Q': 'qtr.',
	'M': 'mo.',
	'W': 'wkly.',
	'D': 'daily'
}
class ForecastPlotter(BasePlotter):

	default_alpha = 0.5

	def __init__(
		self,
		forecast: Forecast,
		method: Union[Callable, str, dict] = ''
	):
		self.forecast_obj = forecast
		self.method = method

	def plot(
		self,
		start: Union[str, bool, Timestamp] = '',
		end: Union[str, bool, Timestamp] = '',
		periods: Union[int, str] = 0,
		**kwargs
	):
		# gather data in the `self.data` attribute & the forecast in `self.fdata`
		self._collect_data()

		if self.method:
			self.data = apply_transformations(self.data, self.method)

		# make the data in all the forecast columns into np.nan so they won't
		#	be shown on top of the actual data
		loi = self.forecast_obj.last_obs_index
		self.data.iloc[:loi, 1:] = np.nan

		if end:
			# if `end` is provided, we just check its somewhere in the forecast
			#	horizon
			lop = self.forecast_obj.last_obs_period
			end_stamp = pd.Timestamp(end)

			if end_stamp > lop:
				self.data = truncate(self.data, start, end_stamp, periods)
			else:
				raise ValueError("value of `end` is not in the forecast horizon")

		else:
			# by default show the last period
			last_period = self.forecast_obj.last_fore_period
			self.data = truncate(self.data, start, last_period, periods)

		# pandas plots consecutive `forecast.plot()` calls on the same axes?
		fig, ax = plt.subplots()

		# remove alpha from kwargs if provided
		alpha = kwargs.pop('alpha', self.default_alpha)

		# use current palette to set colors
		palette = colors.color_palette()
		self.data.iloc[:, 0].plot(ax=ax, color=palette[0], **kwargs)
		self.data.iloc[:, 1:].plot(ax=ax, alpha=alpha, **kwargs)

		return ax

	def _collect_data(self):
		data = get_print_data(self.forecast_obj.data)
		fpaths = self.forecast_obj.paths

		# combine data and the continuous forecast paths in case transformations
		#	are applied that need those past observations
		self.data = pd.concat((data, fpaths), axis='columns').dropna(how='all')

	@property
	def title(self):
		mtype = self.forecast_obj.mtype
		name = self.forecast_obj.obj.long_name.lower()

		if self.forecast_obj.n_paths > 1:
			return ' '.join(['Alternative forecasts of', mtype, name])
		else:
			return ' '.join(['Forecasts of', mtype, name])

	@property
	def entries(self):
		try:
			cols = self.forecast_obj.forecast.columns.tolist()
			cols.insert(0, 'data')
			return cols
		except AttributeError:
			name = self.forecast_obj.forecast.name
			return ['data', name]

	@property
	def n_legend_cols(self):
		return self.forecast_obj.n_paths + 1

class CounterPlotter(object):
	pass
