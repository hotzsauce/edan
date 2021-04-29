"""
module for computing features of GDP data. 'features' are distinct from the
'modifications' in `edan.gdp.modifications` because features involve more
than growth rates or moving averages of a single series - sometimes they even
might involve data from other related GDP compoonents
"""

from __future__ import annotations


from edan.gdp.base import ABCComponent


class Feature(object):
	"""
	Features are intented to be CachedAccessors of Components, or used via the
	methods of the same name that are defined elsewhere in this module
	"""

	def compute(self, *args, **kwargs):
		"""this should be overridden by subclasses"""
		feat = type(self).__name__
		raise NotImplementedError(f"'compute' method not defined for {feat} Feature")

	def __init__(self, obj=None, *args, **kwargs):
		print('initializing Feature: ', type(self).__name__)
		print('obj: ', obj)
		self.obj = obj

	def __call__(self, *args, **kwargs):
		"""
		when called as a method of a Component, i.e.

			>>> gdp = edan.gdp.GDP
			>>> gdp.{feature}()

		the subclass' `compute` method is called & returned
		"""
		return self.compute(*args, **kwargs)


class Nominal(Feature):
	"""
	calculate the nominal level of a GDP component
	"""

	def compute(self, *args, **kwargs):
		component = self.obj

		series = list()
		for attr in ('level', 'price'):
			try:
				data = getattr(component, attr).data
				series.append(data)
			except AttributeError:
				raise AttributeError(
					f"Component '{component.name}' requires '{attr}' GDPSeries to "
					"compute its `nominal` feature"
				) from None

		nom = series[0] * series[1]
		return nom.dropna()


class Contribution(Feature):
	"""
	calculate the percent contribution of subcomponents to the change of
	an aggregate
	"""

	def __call__(
		self,
		subs: Union[list, str] = '',
		*args, **kwargs
	):
		return self.compute(subs, *args, **kwargs)

	def _contr_shares(self):
		""" """
		agg = self.obj
		subs = agg.subcomponents


	def compute(
		self,
		subs: Union[list, str] = '',
		*args, **kwargs
	):

		shares = self._contr_shares()


def nominal(obj):
	""" """
	nom = Nominal(obj)
	return nom.compute()

def contribution(obj, subs: Union[list, str] = ''):
	""" """
	contr = Contribution(obj)
	return contr.compute(subs)
