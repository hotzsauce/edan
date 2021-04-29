"""common utils for datatypes"""

from collections import abc


def iterable_not_string(obj) -> bool:
	"""
	check if the object is an iterable but not a string

	Parameters
	----------
	obj : the object to check

	Returns
	-------
	bool
		whether `obj` is a non-string iterable
	"""
	return isinstance(obj, abc.Iterable) and not isinstance(obj, str)
