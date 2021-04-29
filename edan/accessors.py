"""

"""

from __future__ import annotations


class CachedAccessor:
	"""
	a custom property-like object

	copy of the identically-named class in:
	https://github.com/pandas-dev/pandas/blob/master/pandas/core/accessor.py

	Parameters
	----------
	name : str
		namespace that the property-like object will be accessed under, e.g. `df.foo`
	accessor : cls
		class with extension methods
	"""

	def __init__(self, name: str, accessor) -> None:
		self._name = name
		self._accessor = accessor

	def __get__(self, obj, cls):
		if obj is None:
			#  accessing the attribute of the class
			return self._accessor
		accessor_obj = self._accessor(obj)

		# replace the property with the accessor object. inspired by:
		#	https://www.pydanny.com/cached-property.html
		# we need to use object.__setattr__ because we might overwrite __setattr__
		# elsewhere
		object.__setattr__(obj, self._name, accessor_obj)
		return accessor_obj
