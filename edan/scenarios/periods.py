"""
managing forecast and counterfactual periods
"""


from __future__ import annotations

import numpy as np
import pandas as pd

from edan.utils.ts import infer_freq



def compute_forecast_periods(
	data: Union[pd.Series, pd.DataFrame],
	end: Union[str, Timestamp]
):
	"""
	based on the frequency, compute the number of periods between the last
	observed date and the end of the forecast horizon

	Parameters
	----------
	data : pandas Series | pandas DataFrame
		the observed data
	end : datetime-like str | Timestamp
		the last period of the forecast horizon

	Returns
	-------
	periods : int
	"""
	freq = infer_freq(data)

	# end of horizon; end of data
	end = pd.Timestamp(end)
	ld = data.index[-1]

	if ld > end:
		raise ValueError(
			"last period of forecast horizon must be later than last observation"
		)

	if freq == 'A':
		diff = end.year - ld.year
		return diff if diff > 0 else 1
	elif freq == 'Q':
		# need to make sure both are relative to same starting month
		end = end + pd.tseries.offsets.QuarterBegin(startingMonth=1)
		ld = ld + pd.tseries.offsets.QuarterBegin(startingMonth=1)
		return 4*(end.year - ld.year) + (end.quarter - ld.quarter)
	elif freq == 'M':
		end = end + pd.tseries.offsets.MonthBegin()
		ld = ld + pd.tseries.offsets.MonthBegin()
		return int( (end - ld) / np.timedelta64(1, 'M'))
	elif freq == 'W':
		return int( (end - ld) / np.timedelta64(1, 'W'))
	elif freq == 'D':
		return np.busday_count(ld.date(), end.date())



def compute_forecast_end(data: Union[pd.Series, pd.DataFrame], periods: int):
	"""
	based on the frequency, compute period at the end of the forecast horizon.
	this is returned as a Timestamp, not an actual pandas Period

	Parameters
	----------
	data : pandas Series | pandas DataFrame
		the observed data
	periods : int
		the number of periods in the forecast horizon

	Returns
	-------
	end : pandas Timestamp
	"""

	freq = infer_freq(data)

	# returned Timestamp will be relative to last period of data
	ld = data.index[-1]
	y, m, d = ld.year, ld.month, ld.day

	if freq == 'A':
		return pd.Timestamp(year=y+periods, month=m, day=d)
	elif freq == 'Q':
		return ld + pd.tseries.offsets.QuarterBegin(periods, startingMonth=m)
	elif freq == 'M':
		return ld + pd.tseries.offsets.MonthBegin(periods)
	elif freq == 'W':
		return ld + pd.tseries.offsets.Week(periods, weekday=ld.day_of_week)
	elif freq == 'D':
		return ld + pd.tseries.offsets.BusinessDay(periods)


def default_forecast_horizon(data: Union[pd.Series, pd.DataFrame]):
	"""
	based on the frequency, compute the default number of periods in the forecast
	horizon, and the last period of the horizon (returned as a Timestamp, not an
	actual pandas Period)

	Parameters
	----------
	data : pandas DataFrame
		the observed data

	Returns
	-------
	horizon : tuple(int, pandas Timestamp)
	"""
	_default_periods = {
		'D': 10, # 10 business days, not regular days
		'W': 8,
		'M': 12,
		'Q': 4,
		'A': 2
	}

	freq = infer_freq(data)
	dp = _default_periods[freq]
	return dp, compute_forecast_end(data, dp)
