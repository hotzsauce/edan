"""common utils for datatypes"""

from collections import abc


def is_integer(obj) -> bool:
	"""
	check if the object is an integer

	Parameters
	----------
	obj : the object to check

	Returns
	-------
	is_integer : bool
		whether `obj` is an integer
	"""
	return isinstance(obj, int)


def is_float(obj) -> bool:
	"""
	check if the object is an float

	Parameters
	----------
	obj : the object to check

	Returns
	-------
	is_float : bool
		whether `obj` is an float
	"""
	return isinstance(obj, float)


def iterable_not_string(obj) -> bool:
	"""
	check if the object is an iterable but not a string

	Parameters
	----------
	obj : the object to check

	Returns
	-------
	iterable_not_str : bool
		whether `obj` is a non-string iterable
	"""
	return isinstance(obj, abc.Iterable) and not isinstance(obj, str)


def is_list_like(obj: object, allow_sets: bool = True) -> bool:
	"""
	check if the object is list like.

	objects that are considered list-like are python lists, tuples, sets,
	numpy arrays, and pandas Series and DataFrames. strings and datetime
	objects are not list-like.

	Parameters
	----------
	obj : object
		the object to check
	allow_sets : bool ( = True)
		if this parameter is False, sets are not considered list-like

	Returns
	-------
	is_list_like : bool
		whether `obj` has list-like properties
	"""
	return (
		isinstance(obj, abc.Iterable)
		and not isinstance(obj, (str, bytes))
		# and not np.PyArray_IsZeroDim(obj)
		and not (allow_sets is False and isinstance(obj, abc.Set))
	)


def is_nested_list_like(obj) -> bool:
	"""
	check if the object is list-like, and that all of its elements are also
	list-like

	Parameters
	----------
	obj : the object to check

	Returns
	-------
	is_list_like : bool
		whether `obj` has list-like properties
	"""
	return (
		is_list_like(obj)
		and hasattr(obj, '__len__')
		and len(obj) > 0
		and all(is_list_like(elem) for elem in obj)
	)
