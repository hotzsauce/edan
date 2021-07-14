"""
module for NIPA components
"""

from __future__ import annotations

from edan.accessors import CachedAccessor

from edan.core.series import Series
from edan.core.components import Component
from edan.core.transformations import TransformationAccessor



class CESSeries(Series):

	def __init__(
		self,
		code: str, mtype: str, comp: Component,
		*args, **kwargs
	):
		super().__init__(code, mtype=mtype, source=comp.source, comp=comp)

	# add accessor for functions of data
	transform = CachedAccessor('transform', TransformationAccessor)


class CESComponent(Component):

	mtypes = ['empl_level', 'empl_level_nsa']
	_series_obj = CESSeries
	_default_mtype = 'empl_level'
