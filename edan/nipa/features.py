"""
module for computing features of GDP data. 'features' are distinct from the
'modifications' in `edan.gdp.modifications` because features involve more
than growth rates or moving averages of a single series - sometimes they even
might involve data from other related GDP compoonents
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class Feature(object):
	"""
	Features are intented to be CachedAccessors of Components, or used via the
	methods of the same name that are defined elsewhere in this module
	"""

	name = ''

	def compute(self, *args, **kwargs):
		"""this should be overridden by subclasses"""
		feat = type(self).__name__
		raise NotImplementedError(f"'compute' method not defined for {feat} Feature")

	def __init__(self, obj=None, *args, **kwargs):
		print('initializing Feature: ', type(self).__name__)
		self.obj = obj

	def __call__(self, *args, **kwargs):
		"""
		when called as a method of a Component, i.e.

			>>> gdp = edan.nipa.GDPTable['gdp']
			>>> gdp.{feature}()

		the subclass' `compute` method is called & returned
		"""
		return self.compute(*args, **kwargs)


class Contribution(Feature):
	"""
	calculate the percent contribution of subcomponents to the change of
	an aggregate
	"""

	name = 'contr'

	def __call__(
		self,
		subs: Union[list, str] = '',
		*args, **kwargs
	):
		return self.compute(subs, *args, **kwargs)

	def _contr_shares(self):
		"""
		https://apps.bea.gov/scb/account_articles/national/0795od/maintext.htm
		https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm
		"""

		ragg = self.obj.real.data
		nagg = self.obj.nominal.data
		subs = self.obj.subs

		# let pandas handle all the joining & nan-creation for observations where
		#	some series don't have values
		real = pd.concat([ragg] + [sub.real.data for sub in subs], axis='columns')
		nominal = pd.concat([nagg] + [sub.nominal.data for sub in subs], axis='columns')
		data = pd.concat([real, nominal], axis='columns').dropna(axis='index')

		# re-partition data; each block has the aggregate series in the first col
		real = data.iloc[:, :len(subs)+1].values
		nominal = data.iloc[:, len(subs)+1:].values

		# implied nominal level as if there were no price changes
		rgrowth = real[1:, :] / real[:-1, :]
		nan_row = np.empty((1, rgrowth.shape[1]))
		nan_row[:] = np.nan

		rgrowth = np.vstack((nan_row, rgrowth))
		imp_nom = np.multiply(rgrowth, nominal)

		# calculate the shares: (imp_nom - nom)/(imp_agg - agg)
		agg_chg = imp_nom[1:, 0] - nominal[:-1, 0]
		sub_chg = imp_nom[1:, 1:] - nominal[:-1, 1:]
		shares = np.divide(sub_chg, agg_chg[:, None]) # index allows for broadcast

		# add the nans into the first row, format into DataFrame with edan codes
		#	of components as column names
		nan_row = np.empty((1, shares.shape[1]))
		nan_row[:] = np.nan
		shares = np.vstack((nan_row, shares))

		return pd.DataFrame(shares, index=data.index, columns=[s.code for s in subs])


	def compute(
		self,
		subs: Union[list, str] = '',
		method: str = 'difa%',
		*args, **kwargs
	):
		if not self.obj.subs:
			# if component has no subcomponent, return pandas Series of ones
			return pd.Series(
				data=np.ones(len(self.obj.real.data)),
				index=self.obj.real.data.index,
				name=self.name
			)

		# compute the aggregate growth rate and the shares of each subcomponent
		agg_growth = self.obj.real.modify(method, *args, **kwargs)
		shares = self._contr_shares()

		# odds are the shares will only have a subset of the observations
		data = pd.concat((agg_growth, shares), axis='columns').dropna(axis='index')

		# final step is product of aggregate growth rate and computed shares
		agg = data.iloc[:, 0].values
		shares = data.iloc[:, 1:].values
		contr = np.multiply(shares, agg[:, None]) # index allows for broadcast

		return pd.DataFrame(
			contr,
			index=data.index,
			columns=[f"{s.code}_{self.name}" for s in self.obj.subs]
		)


def contribution(obj, subs: Union[list, str] = ''):
	""" """
	contr = Contribution(obj)
	return contr.compute(subs)
