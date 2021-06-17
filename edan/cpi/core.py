"""
module for CPI components
"""

from edan.accessors import CachedAccessor

from edan.core.series import Series
from edan.core.components import Component
from edan.core.transformations import TransformationAccessor


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
