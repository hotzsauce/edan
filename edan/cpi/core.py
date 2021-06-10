"""
module for CPI components
"""

from edan.accessors import CachedAccessor

from edan.aggregates.series import Series
from edan.aggregates.components import Component
from edan.aggregates.transformations import TransformationAccessor

from edan.plotting.generic import ComponentPlotter


class CPISeries(Series):

	def __init__(
		self,
		code: str, mtype: str, obj: Component,
		*args, **kwargs
	):
		super().__init__(code, source=obj.source)

		self.mtype = mtype
		self.obj = obj

	# add accessor for functions of data
	transform = CachedAccessor('transform', TransformationAccessor)

class CPIComponent(Component):

	mtypes = ['price']
	_series_obj = CPISeries
	_default_mtype = 'price'

	# add accessor for plotting
	plot = CachedAccessor('plot', ComponentPlotter)
