

from __future__ import annotations

import numpy as np
import pandas as pd

from edan.core.base import (
	BaseSeries,
	BaseComponent
)

from edan.accessors import CachedAccessor
from edan.plotting.scenarios import ForecastPlotAccessor

from edan.utils.ts import (
	infer_freq,
	periods_per_year
)

from edan.scenarios.base import BaseForecast
from edan.scenarios.periods import (
	compute_forecast_periods,
	compute_forecast_end,
	default_forecast_horizon
)



class Forecast(BaseForecast):

	@property
	def last_fore_period(self):
		""" return the last period in the forecast """
		return self.forecast.index[-1]

	@property
	def last_fore_index(self):
		""" return the last integer location """
		return self.last_obs_index + len(self.forecast.index) - 1

	@property
	def last_obs_period(self):
		""" return the last period for which there's an observation """
		return self.data.index[-1]

	@property
	def last_obs_index(self):
		""" return the last integer location for which there's an observation """
		return len(self.data.index) - 1

	@property
	def n_paths(self):
		""" return the number of individual forecast paths """
		if self.forecast.ndim > 1:
			return self.forecast.shape[1]
		return 1

	@property
	def n_fperiods(self):
		""" return the number of periods in the forecast """
		return self.forecast.shape[0]

	@property
	def paths(self):
		"""
		concatenate the observed data & forecast data into 'continuous' forecast
		paths DataFrame/Series
		"""
		# number of data observations, forecast periods & forecast paths
		n_obs, n_fps = len(self.data.index), len(self.forecast.index)
		n_paths = self.n_paths

		# combine indices into full path index
		idx = self.data.index.union(self.forecast.index)

		# filling in observed data
		arr = np.empty((n_obs + n_fps, n_paths))
		arr[:n_obs] = self.data.to_numpy()[..., np.newaxis]

		# taking into account numpy vector vs numpy 2d-matrix
		if n_paths == 1:
			arr[n_obs:] = self.forecast.to_numpy()[..., np.newaxis]
			return pd.Series(arr.flatten(), index=idx, name=self.forecast.name)
		else:
			arr[n_obs:] = self.forecast.to_numpy()
			return pd.DataFrame(arr, index=idx, columns=self.forecast.columns)

	# accessor for plotting
	plot = CachedAccessor('plot', ForecastPlotAccessor)



def forecast(
	obj: Union[Series, Component],
	fore: Union[float, Sequence[float]] = 0.0,
	method: str = 'difa%',
	mtype: str = '',
	periods: int = 0,
	end: str = '',
	orient: str = 'columns',
	labels: Union[str, Sequence[str]] = ''
):
	"""
	creates a Forecast of either a Series or Component

	Parameters
	----------
	obj : Series | Component
		the edan object whose data will be used in the forecast computation
	fore : float | array ( = 0.0 )
		the forecasted information. the units/interpretation depend on the
		`method` parameter. if an array, the length determines the number of
		periods that will be forecast
	method : str ( = 'difa%' )
		the type of forecast information that is passed to the `fore` parameter.
		this determines the forecasting formula used. most of the methods that
		can be used to transform data are available
	mtype : str ( = '' )
		measure type to forecast. if not provided & `obj` is a Component,
		its default_mtype will be used
	periods : int ( = 0 )
		the number of periods to forecast through, if `fore` is a float. if
		provided, and `fore` is an array whose length does not equal `periods`,
		a ValueError is thrown.
	end : datetime-like str | Timestamp ( = '' )
		the last period of the forecast horizon. a ValueError is thrown if both
		`periods` and `end` are provided
	orient : str ( = 'columns' )
		if `fore` is multi-dimensional - meaning more than one Component/Series
		will be forecast - this determines how to interpret the array. accepted
		values are 'columns' and 'rows'. when `orient='columns'`, the i-th column
		of `fore` is applied to the i-th forecast object. the case for
		`orient='rows'` is analagous
	labels : str | Sequence[str] ( = '' )
		the labels of the forecasts. if the forecast values are multi-dimensional,
		then the length of `labels` (if provided) should be equal to the number
		of forecasts, which will be determined by the `orient` parameter. if not
		provided, default label for single-dimension forecasts is 'forecast' and
		for multi-dimensional, is 'forecast{i}'
	"""
	forecaster = Forecaster(fore, method, periods, end, orient, labels)
	return forecaster.create_forecast(obj, mtype=mtype)



class Forecaster(object):
	"""
	factory-type class to create Forecast objects

	Parameters
	----------
	fore : float | array | pandas Series | pandas DataFrame ( = 0.0 )
		the forecasted information. the units/interpretation depend on the
		`method` parameter. if an array or pandas object, the length determines
		the number of periods that will be forecast. if a pandas object &
		`orient='columns'`, the name/columns will be used to label the forecast(s).
		if a pandas object & `orient='rows'` the index is used
	method : str ( = 'difa%' )
		the type of forecast information that is passed to the `fore` parameter.
		this determines the forecasting formula used. most of the methods that
		can be used to transform data are available
	periods : int ( = 0 )
		the number of periods to forecast through, if `fore` is a float. if
		provided, and `fore` is an array whose length does not equal `periods`,
		a ValueError is thrown.
	end : datetime-like str | Timestamp ( = '' )
		the last period of the forecast horizon. a ValueError is thrown if both
		`periods` and `end` are provided
	orient : str ( = 'columns' )
		if `fore` has dimension > 1, this determines how to interpret the array.
		accepted values are 'columns' and 'rows'. when `orient='columns'`, the
		i-th column of `fore` is applied to the i-th forecast object. the case
		for `orient='rows'` is analagous
	labels : str | Sequence[str] ( = '' )
		the labels of the forecasts. if the forecast values are multi-dimensional,
		then the length of `labels` (if provided) should be equal to the number
		of forecasts, which will be determined by the `orient` parameter. if not
		provided, default label for single-dimension forecasts is 'forecast' and
		for multi-dimensional, is 'forecast{i}'
	"""

	def __init__(
		self,
		fore: Union[float, Sequence[float]] = 0.0,
		method: str = 'difa%',
		periods: int = 0,
		end: Union[str, Timestamp] = '',
		orient: str = 'columns',
		labels: Union[str, Sequence[str]] = ''
	):
		self.fore = fore
		self.method = method

		if periods and end:
			raise ValueError("only one of `periods` and `end` can be specified")

		if np.ndim(fore) == 0:
			self.periods = periods
			self.labels = labels if labels else 'forecast'
			self.fore = np.array(fore)

		elif np.ndim(fore) == 1:
			if orient not in ('columns', 'rows'):
				raise ValueError(
					"accepted values of `orient` are 'columns' and 'rows'"
			)

			if orient == 'rows':
				# with 1-dim `fore`, setting `orient='rows'` basically means
				#	len(fore) 1-period forecasts

				if isinstance(fore, pd.Series):
					# can't do `try: fore.index except ...` b/c list type has
					#	`index` method
					fore_labels = fore.index
				else:
					fore_labels = [f"forecast{i}" for i in range(len(fore))]

				self.labels = labels if labels else fore_labels
				self.fore = np.transpose(np.array(fore))[np.newaxis, ...]

			else:
				# with `orient='columns'`, it's a single len(fore)-period forecast
				try:
					series_name = fore.name
				except AttributeError:
					series_name = 'forecast'

				self.labels = labels if labels else series_name
				self.fore = np.array(fore)


		elif np.ndim(fore) == 2:
			if orient not in ('columns', 'rows'):
				raise ValueError(
					"accepted values of `orient` are 'columns' and 'rows'"
			)

			fore_arr = np.array(fore)

			if orient == 'rows':
				try:
					fore = fore.transpose()
				except AttributeError:
					# `fore` is list-of-lists
					pass
				fore_arr = np.transpose(fore_arr)

			try:
				columns = fore.columns
			except AttributeError:
				columns = [f"forecast{i}" for i in range(fore_arr.shape[1])]

			if fore_arr.shape[1] == 1:
				# 1-column DataFrame or 2-d numpy array vector
				self.labels = columns[0]
				self.fore = fore_arr.flatten()
			else:
				self.labels = labels if labels else columns
				self.fore = fore_arr

		else:
			raise ValueError("`fore` must be a scalar, or have ndims <= 2")

		if np.ndim(self.fore) >= 1:
			# same check for ndim == 1 and ndim == 2
			if (periods != 0) and (len(self.fore) != periods):
				raise ValueError(
					f"length of `fore` implies number of periods {len(self.fore)};"
					f" provided `periods` parameter is {periods}"
				)
			else:
				self.periods = len(self.fore)

		self.end = end

	def create_forecast(
		self,
		obj: Union[Series, Component],
		mtype: str = ''
	):
		"""
		create a Forecast object using the `fore` that were used to instantiate
		this Forecaster object.

		Parameters
		----------
		obj : Series | Component
			the edan object whose data will be used in the forecast computation
		mtype : str ( = '' )
			measure type to forecast. if not provided & `obj` is a Component,
			its default_mtype will be used

		Returns
		-------
		Forecast
		"""

		if isinstance(obj, BaseSeries):
			if mtype:
				raise ValueError(
					"`mtype` parameter cannot be provided when forecasting Series"
				)
			data = obj.data
			mtype = obj.mtype

		elif isinstance(obj, BaseComponent):
			if mtype:
				series_obj = getattr(obj, mtype)
				data = series_obj.data
			else:
				data = obj.default_mtype.data
				mtype = obj._default_mtype

		else:
			raise NotImplementedError("can only forecast single Series or Components")

		# if `self.fore` is a scalar and both `self.periods` and `self.end` were
		#	not provided, data frequency determines number of forecast periods. if
		#	one is provided, that determines the number
		if np.ndim(self.fore) == 0:
			if self.periods:
				fperiods = self.periods
			elif self.end:
				fperiods = compute_forecast_periods(data, self.end)
			else:
				fperiods, _ = default_forecast_horizon(data)

		else:
			fperiods = self.periods

		try:
			fmethod = FORECAST_FORMULAS[self.method]
			fdata = _compute_forecast_data(data, fmethod, self.fore, fperiods)
		except KeyError:
			raise ValueError(
				f"unrecognized value for `method`: {self.method}"
			) from None

		if isinstance(fdata, pd.Series):
			fdata.name = self.labels
		elif isinstance(fdata, pd.DataFrame):
			fdata.columns = self.labels

		return Forecast(obj, fdata, mtype)



def _compute_forecast_data(
	data: Union[pd.Series, pd.DataFrame],
	fmethod: Callable,
	finfo: np.ndarray,
	periods: int
):
	"""
	compute the forecast data given the observed data, forecast method, and
	forecast information.

	Parameters
	----------
	data : pandas Series | pandas DataFrame
		the observed data used to create a forecast. the `pandas.infer_freq` method
		is called on `data`'s Index, so the data must have evenly-spaced observations
	fmethod : Callable
		the function used to create the forecast data. it must accept three arguments:
			1) `data`
			2) the `finfo` parameter
			3) the `periods` parameter
	finfo : np.ndarray
		forecast information used in the `fmethod` function. for example, this would
		be the forecasted growth rates of `data`
	periods : int
		the number of periods to be forecast

	Returns
	-------
	forecast : pandas Series | pandas DataFrame
		if np.ndim(finfo) > 1, returns DataFrame. otherwise, returns Series
	"""
	fdata = fmethod(data, finfo, periods)

	idx = pd.date_range(
		start=data.index[-1],
		periods=periods+1,
		freq=pd.infer_freq(data.index)
	)

	if np.ndim(fdata) <= 1:
		forecast = pd.Series(fdata, index=idx[1:])
	else:
		forecast = pd.DataFrame(fdata, index=idx[1:])

	return forecast



# formulas for different methods of forecasting
def diff(data, fore, periods):
	"""
	period-to-period change
		x(t) = x(t-1) + fore(t)
	"""
	if np.ndim(fore) == 0:
		# `fore` is just a single float
		changes = np.full(periods, fore)
	else:
		# `fore` is a vector or array
		changes = fore

	return data.iloc[-1] + changes

def diffp(data, fore, periods):
	"""
	period-to-period percent change
		x(t) = x(t-1) * (1 + fore(t)/100)
	"""
	if np.ndim(fore) == 0:
		base = np.ones(periods) + fore / 100
		factor = np.power(base, np.arange(periods) + 1)
	else:
		base = np.ones(fore.shape) + fore / 100
		factor = np.cumprod(base, axis=0)

	return data.iloc[-1] * factor

def diffl(data, fore, periods):
	"""
	period-to-period log change
		x(t) = x(t-1) * exp( fore(t)/100 )
	"""
	if np.ndim(fore) == 0:
		factor = np.exp( (np.arange(periods) + 1) * (fore/100) )
	else:
		period_factors = np.exp( fore/100 )
		factor = np.cumprod(period_factors, axis=0)

	return data.iloc[-1] * factor

def difa(data, fore, periods):
	"""
	period-to-period annualized change
		x(t) = x(t-1) + fore(t) / h
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		changes = np.full(periods, fore / h)
	else:
		changes = fore / h

	return data.iloc[-1] + changes

def difap(data, fore, periods):
	"""
	annualized percent change period-to-period
		x(t) = x(t-1) * (1 + fore(t)/100)^(1/h)
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		base = np.ones(periods) + fore / 100
		factor = np.power(base, (np.arange(periods) + 1) / h)
	else:
		base = np.ones(fore.shape) + fore / 100
		period_factors = np.power(base, 1 / h)
		factor = np.cumprod(period_factors, axis=0)

	return data.iloc[-1] * factor

def difal(data, fore, periods):
	"""
	annualized log change period-to-period
		x(t) = x(t-1) * exp( fore(t) / (100*h) )
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		factor = np.exp( (np.arange(periods) + 1) * fore/(100*h) )
	else:
		period_factors = np.exp( fore / (100*h) )
		factor = np.cumprod(period_factors, axis=0)

	return data.iloc[-1] * factor

def yryr(data, fore, periods):
	"""
	year-over-year change
		x(t) = x(t-h) + fore(t)
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		changes = np.full(periods, fore)
	else:
		changes = fore

	# `changes` entries are overwritten, and `data` entries will be cast
	#	to `changes` dtypes, so if `changes` is a single integer, `data` values
	#	will be rounded to nearest int, which we obviously don't want
	try:
		dtype = data.dtype
		if not dtype:
			dtype = 'float64'
	except:
		dtype = 'float64'
	changes = changes.astype(dtype)

	for i in range(periods):
		if i < h:
			changes[i] = data.iloc[-h+i] + changes[i]
		else:
			changes[i] = changes[-h+i] + changes[i]

	return changes

def yryrp(data, fore, periods):
	"""
	year-over-year percent change
		x(t) = x(t-h) * (1 + fore(t)/100)
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		rates = np.full(periods, fore)
	else:
		rates = fore

	# `rates` entries are overwritten, and `data` entries will be cast
	#	to `rates` dtypes, so if `rates` is a single integer, `data` values
	#	will be rounded to nearest int, which we obviously don't want
	try:
		dtype = data.dtype
		if not dtype:
			dtype = 'float64'
	except:
		dtype = 'float64'
	rates = rates.astype(dtype)

	for i in range(periods):
		if i < h:
			rates[i] = data.iloc[-h+i] * (1 + rates[i]/100)
		else:
			rates[i] = rates[-h+i] * (1 + rates[i]/100)

	return rates


def yryrl(data, fore, periods):
	"""
	year-over-year log change
		x(t) = x(t-h) * exp( fore(t)/100 )
	"""
	h = periods_per_year(data)

	if np.ndim(fore) == 0:
		rates = np.full(periods, fore)
	else:
		rates = fore

	# `rates` entries are overwritten, and `data` entries will be cast
	#	to `rates` dtypes, so if `rates` is a single integer, `data` values
	#	will be rounded to nearest int, which we obviously don't want
	try:
		dtype = data.dtype
		if not dtype:
			dtype = 'float64'
	except:
		dtype = 'float64'
	rates = rates.astype(dtype)

	for i in range(periods):
		if i < h:
			rates[i] = data.iloc[-h+i] * np.exp( rates[i]/100 )
		else:
			rates[i] = rates[-h+i] * np.exp( rates[i]/100 )

	return rates


FORECAST_FORMULAS = {
	'diff': diff,
	'diff%': diffp,
	'diffl': diffl,
	'difa': difa,
	'difa%': difap,
	'difal': difal,
	'yryr': yryr,
	'yryr%': yryrp,
	'yryrl': yryrl
}
