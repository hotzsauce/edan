"""
first pass at an economic data analysis toolkit, with some vague intent to learn
more about the NIPA/PCE accounts, and financial markets - specifically treasuries
and other interest rate-related markets

'edan' <- e(conomic) d(ata) an(alysis)
"""

import edan.nipa
import edan.cpi
import edan.ces
import edan.data
import edan.plotting

from edan.aggr import aggregate

from edan.core.transformations import transform

from edan.scenarios.forecasts import (
	forecast,
	Forecast,
	Forecaster
)

from edan.indices import (
	paasche,
	laspeyres,
	fisher,
	tornqvist,
	walsh,
	geometric
)



__all__ = [
	# modules
	'nipa',
	'cpi',
	'ces',
	'data',
	'plotting',

	# modifications
	'transform',

	# counterfactuals & foreasts
	'forecast',
	'Forecast',
	'Forecaster',

	# indices
	'paasche',
	'laspeyres',
	'fisher',
	'tornqvist',
	'walsh',
	'geometric',
	'marshall_edgeworth',
	'carli',
	'dutot',
	'jevons',
	'harmonic_mean',
	'cswd_index',
	'harmonic_ratio'
]
