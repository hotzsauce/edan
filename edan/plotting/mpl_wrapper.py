"""
wrapping the matplotlib.pyplot package so the user doesn't have to import
both `edan` and `matplotlib.pyplot`
"""

import matplotlib.pyplot as _plt

_all_ = list()
def wrap_namespace(old, new):

	for name, obj in old.items():
		_all_.append(name)
		new[name] = obj

wrap_namespace(_plt.__dict__, globals())
__all__ = _all_
