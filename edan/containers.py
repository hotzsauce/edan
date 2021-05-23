"""
module for base classes of data objects in edan.

CompoundStorage - base class of GDP components
"""

from edan.base import EdanObject

from edan.indexing import CompoundAccessor


class CompoundStorage(CompoundAccessor, EdanObject):

	def __init__(self, fields):
		super().__init__(fields=fields)
