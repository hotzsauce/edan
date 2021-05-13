"""
module for base classes of data objects in edan.

CoreSeries		- base class of GDP & financial series
CompoundStorage - base class of GDP components
"""

from edan.base import EdanObject

from edan.indexing import CompoundAccessor


class CoreSeries(EdanObject):

	def __init__(self, code='', data=None):
		self.code = code
		self.data = data

	def resample(self, rule, **kwargs):
		"""
		pseudo-wrapper function for pandas resample() method. adds functionality
		for in-place modifications of `data` with the 'inplace' kwarg. if
		'inplace' is provided, the `data` attribute is modifided and nothing is
		returned. otherwise, `data` is left untouched and a new CoreSeries object
		with the altered `data` attribute is returned.

		Parameters
		----------
		rule : DateOffset | TimeDelta | str
			the offset string or object representing target conversion
		kwargs : dict
			keyword arguments as specified in the documentation for the pandas
			resample() method:
				https://pandas.pydata.org/pandas-doc/stable/reference/api/
				pandas.DataFrame.resample.html
			as mentioned above, an `inplace` keyword argument is available for
			CoreSeries, which is not available for normal Pandas Series

		Returns
		-------
		CoreSeries or None
		"""
		inplace = kwargs.pop('inplace', False)
		try:
			if inplace:
				self.data = self.data.resample(rule, **kwargs)
				return None
			else:
				return CoreSeries(self.code, self.data.resample(rule, **kwargs))

		except AttributeError:
			raise ValueError(f"CoreSeries {repr(self.code)} has no data to resample")


class CompoundStorage(CompoundAccessor, EdanObject):

	def __init__(self, fields):
		super().__init__(fields=fields)
