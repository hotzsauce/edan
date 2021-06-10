"""
module for computing features of CPI data. 'features' are distinct from the
'transformations' in `edan.aggregates.transformations` because features involve
more than growth rates or moving averages of a single series - sometimes they
even might involve data from other related CPI components
"""

from __future__ import annotations

from edan.aggregates.transformations import Feature

class Share(Feature):
	pass
