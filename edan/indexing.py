"""
accessing underlying pandas Series and DataFrames of edan data objects
"""

from __future__ import annotations

import pandas as pd

class _GenericIndexer(object):

	def __init__(self, name, obj):
		self.name = name
		self.obj = obj

	def concat(self, objs):

		series = []
		for o in objs:
			# if a field has no data, make empty series before concatenating
			if o is None:
				series.append(pd.Series())
			else:
				series.append(o)

		return pd.concat(series, axis='columns', join='outer')



class _iLocIndexer(_GenericIndexer):
	"""
	accessing data in underlying fields by index locations
	"""
	def __getitem__(self, key):

		data = [getattr(self.obj, f).data for f in self.obj.fields]

		df = self.concat(data)
		df.columns = self.obj.fields
		return df.iloc[key]



class _LocIndexer(_GenericIndexer):
	"""
	accessing data in underlying fields by index keys
	"""
	def __getitem__(self, key):
		data = [getattr(self.obj, f).data for f in self.obj.fields]

		df = self.concat(data)
		df.columns = self.obj.fields
		return df.loc[key]



class CompoundAccessor(object):
	"""
	originally conceived to allow for selecting data from the level and price
	series of a GDP component with a single line. lets user use pandas-like
	`.loc` and `.iloc` accessors on an object with a single or many pandas Series
	or DataFrames in its attributes
	"""

	def __init__(self, fields):
		self.fields = fields

	@property
	def iloc(self):
		return _iLocIndexer('iloc', self)

	@property
	def loc(self):
		return _LocIndexer('loc', self)
