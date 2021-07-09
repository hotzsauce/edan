"""
first pass at an economic data analysis toolkit, with some vague intent to learn
more about the NIPA/PCE accounts, and financial markets - specifically treasuries
and other interest rate-related markets

'edan' <- e(conomic) d(ata) an(alysis)
"""

import edan.nipa
import edan.cpi
import edan.data
import edan.plotting

from edan.core.transformations import transform

from edan.scenarios.forecasts import (
	forecast,
	Forecast,
	Forecaster
)


__all__ = [
	'nipa',
	'cpi',
	'data',
	'plotting',
	'transform',
	'forecast',
	'Forecast',
	'Forecaster'
]
