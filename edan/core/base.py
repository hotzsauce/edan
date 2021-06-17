"""
base Series and Component classes. needed for partial imports of edan
modules and type checks
"""

from edan.base import EdanObject
from edan.containers import CompoundStorage

class BaseSeries(EdanObject):
	pass

class BaseComponent(CompoundStorage):
	pass
