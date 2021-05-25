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
		level: int = 0,
		*args, **kwargs
	):
		return self.compute(subs, level, *args, **kwargs)

	def _contr_shares(self, subs: Disaggregator):
		"""
		the calculation for the contribution shares is described in the footnotes
		of this table:
			https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

		that table is referenced in this old article from the BEA, along with
		some discussion about other new (in 1995) measures:
			https://apps.bea.gov/scb/account_articles/national/0795od/maintext.htm
		"""

		ragg = self.obj.real.data
		nagg = self.obj.nominal.data

		# let pandas handle all the joining & nan-creation for observations where
		#	some series don't have values
		real_data, nom_data, sub_names = [ragg], [nagg], []
		for sub in subs:
			rsub = sub.real.data
			nsub = sub.nominal.data

			# if there is no real or nominal data, just exclude it for now
			if (rsub is None) or (nsub is None):
				pass
			else:
				real_data.append(rsub)
				nom_data.append(nsub)
				sub_names.append(sub.code)

		real = pd.concat(real_data, axis='columns')
		nominal = pd.concat(nom_data, axis='columns')
		data = pd.concat([real, nominal], axis='columns').dropna(axis='index')

		# re-partition data; each block has the aggregate series in the first col
		n_series = len(real_data)
		real = data.iloc[:, :n_series].values
		nominal = data.iloc[:, n_series:].values

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

		return pd.DataFrame(shares, index=data.index, columns=sub_names)

	def compute(
		self,
		subs: Union[list, str] = '',
		level : int = 0,
		method: str = 'difa%',
		*args, **kwargs
	):
		"""
		compute & return a dataframe of subcomponents' contributions to percent
		change of an aggregate. the calculations are described in the footnotes
		of this table:
			https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

		by default, the contributions from all direct subcomponents are computed,
		but this can be changed via the `subs` parameter.

		Parameters
		----------
		subs : list | str ( = '' )
			the subcomponents to include in the calculation. if an empty string,
			all immediate subcomponents are used (if the other subcomponent
			selection parameters, for example, `level`, are null). otherwise, the
			subcomponent selection is done by the Component's `disaggregate()`
			method
		level : int ( = 0 )
			the level of subcomponents to include in the calculation
		method : str ( = 'difa%' )
			the growth rate calculation of the aggregate real level. see the
			Modifications class in edan/nipa/modifications.py for details.
		args : positional arguments
			arguments to pass to the `modify()` method of the aggregates's real level
		kwargs : keyword arguments
			arguments to pass to the `modify()` method of the aggregates's real level

		Returns
		-------
		pandas DataFrame
		"""
		if not self.obj.subs:
			# if component has no subcomponent, return pandas Series of ones
			return pd.Series(
				data=np.ones(len(self.obj.real.data)),
				index=self.obj.real.data.index,
				name=self.name
			)

		# compute the aggregate growth rate
		agg_growth = self.obj.real.modify(method, *args, **kwargs)

		# compute the shares of each subcomponent
		subs = self.obj.disaggregate(subs, level)
		shares = self._contr_shares(subs)

		# odds are the shares will only have a subset of the observations
		data = pd.concat((agg_growth, shares), axis='columns').dropna(axis='index')

		# final step is product of aggregate growth rate and computed shares
		agg = data.iloc[:, 0].values
		contr_shares = data.iloc[:, 1:].values
		contr = np.multiply(contr_shares, agg[:, None]) # index allows for broadcast

		return pd.DataFrame(
			contr,
			index=data.index,
			columns=shares.columns
		)


def contribution(
	obj,
	subs: Union[list, str] = '',
	level: int = 0,
	*args, **kwargs
):
	"""
	compute & return a dataframe of subcomponents' contributions to percent
	change of an aggregate. the calculations are described in the footnotes
	of this table:
		https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

	by default, the contributions from all direct subcomponents are computed,
	but this can be changed via the `subs` parameter.

	Parameters
	----------
	subs : list | str ( = '' )
		the subcomponents to include in the calculation. if an empty string,
		all immediate subcomponents are used (if the other subcomponent
		selection parameters, for example, `level`, are null). otherwise, the
		subcomponent selection is done by the Component's `disaggregate()`
		method
	level : int ( = 0 )
		the level of subcomponents to include in the calculation
	method : str ( = 'difa%' )
		the growth rate calculation of the aggregate real level. see the
		Modifications class in edan/nipa/modifications.py for details.
	args : positional arguments
		arguments to pass to the `modify()` method of the aggregates's real level
	kwargs : keyword arguments
		arguments to pass to the `modify()` method of the aggregates's real level

	Returns
	-------
	pandas DataFrame
	"""
	contr = Contribution(obj)
	return contr.compute(subs, level, *args, **kwargs)
