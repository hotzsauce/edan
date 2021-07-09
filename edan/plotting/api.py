"""
plotting module-level `plot` function that generalizes matplotlib's `plot`
method to handle visualizations of `edan` objects
"""

from __future__ import annotations

import matplotlib.pyplot as plt

from edan.errors import FeatureError

from edan.plotting.generic import plot_on_canvas
from edan.plotting.features import get_feature

from edan.core.base import (
	BaseSeries,
	BaseComponent
)
from edan.plotting.core import (
	SeriesPlotter,
	ComponentPlotter
)

from edan.scenarios.base import BaseForecast
from edan.plotting.scenarios import ForecastPlotter


def plot(
	obj,
	**kwargs
):
	if isinstance(obj, BaseComponent):
		subs = kwargs.pop('subs', True)
		level = kwargs.pop('level', 0)
		mtype = kwargs.pop('mtype', '')
		method = kwargs.pop('method', '')
		feature = kwargs.pop('feature', '')

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
		return plot_on_canvas(plotter, **kwargs)

	elif isinstance(obj, BaseForecast):
		method = kwargs.pop('method', '')

		plotter = ForecastPlotter(
			forecast=obj,
			method=method
		)
		return plot_on_canvas(plotter, **kwargs)

	else:
		# if something was plotted earlier in the script, `obj` is plotted on
		#	that axes for some reason?
		fig, ax = kwargs.pop('figure', None), kwargs.pop('ax', None)

		if (not fig) and (not ax):
			fig, ax = plt.subplots()
		elif fig:
			ax = plt.gca()
		elif ax:
			fig = plt.gcf()

		# create axes & return just the axes to maintain consistency with the
		#	plot_on_canvas method
		_ = plt.plot(obj, **kwargs)
		return plt.gca()
