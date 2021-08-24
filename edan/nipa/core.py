"""
module for NIPA components
"""

from __future__ import annotations

from edan.accessors import CachedAccessor

from edan.core.series import Series
from edan.core.components import (
	Component,
	FlowComponent,
	BalanceComponent
)
from edan.core.transformations import TransformationAccessor

from edan.nipa.features import (
	Contribution,
	Share
)


class NIPASeries(Series):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	# add accessor for functions of data
	transform = CachedAccessor('transform', TransformationAccessor)


class NIPAComponent(Component):

	mtypes = ['quantity', 'price', 'nominal', 'real', 'nominal_level', 'real_level']
	_series_obj = NIPASeries
	_default_mtype = 'real'

	# add accessors for common features
	contributions = CachedAccessor('contributions', Contribution)
	shares = CachedAccessor('shares', Share)


class NIPAFlowComponent(NIPAComponent, FlowComponent):
	pass

class NIPABalanceComponent(NIPAComponent, BalanceComponent):
	pass

def component_type(ctype: str):
	"""
	used in edan/nipa/api.py when constructing the PCE and GDP tables
	"""
	if ctype == 'stock':
		return NIPAComponent
	elif ctype == 'flow':
		return NIPAFlowComponent
	elif ctype == 'balance':
		return NIPABalanceComponent

	raise ValueError(ctype)
