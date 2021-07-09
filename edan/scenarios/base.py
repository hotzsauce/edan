"""
base objects for forecast outlooks and counterfactuals
"""

from __future__ import annotations

from edan.base import EdanObject

from edan.core.base import (
	BaseSeries,
	BaseComponent
)

from edan.scenarios.periods import (
	compute_forecast_periods,
	compute_forecast_end,
	default_forecast_horizon
)

class BaseForecast(EdanObject):
	"""
	base object for Series and Component forecasts. needed to prevent partial
	imports, and also used to manage Series/Components interface differences
	"""

	def __init__(
		self,
		obj: Union[Series, Component],
		forecast: Union[pd.Series, pd.DataFrame],
		mtype: str = ''
	):
		self.obj = obj
		self.mtype = mtype

		if isinstance(self.obj, BaseSeries):
			self.data = self.obj.data
			if not self.mtype:
				self.mtype = self.obj.mtype

		elif isinstance(self.obj, BaseComponent):
			if self.mtype:
				series_obj = getattr(self.obj, self.mtype)
				self.data = series_obj.data

			else:
				self.data = self.obj.default_mtype.data
				self.mtype = self.obj._default_mtype

		self.forecast = forecast

	def __repr__(self):
		return f"{type(self).__name__}({self.obj})"
