"""
module for computing features of NIPA data. 'features' are distinct from the
'modifications' in `edan.aggregates.modifications` because features involve more
than growth rates or moving averages of a single series - sometimes they even
might involve data from other related NIPA components
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.aggregates.components import (
	FlowComponent,
	BalanceComponent
)

from edan.aggregates.modifications import Feature



class Contribution(Feature):
	"""
	calculate the percent contribution of subcomponents to the change of
	an aggregate
	"""

	name = 'contr'

	def __call__(
		self,
		subs: Union[list, str, bool] = '',
		level: int = 0,
		method: Union[str, Callable] = '',
		*args, **kwargs
	):
		"""
		compute & return a dataframe of subcomponents' contributions to percent
		change of an aggregate. the calculations are described in the footnotes
		of this table:
			https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

		by default, the contribution from all direct subcomponents are computed,
		but this can be changed via the `subs` and `level` parameters

		Parameters
		----------
		subs : list | str ( = '' )
			the subcomponents to include in the calculation. if an empty string,
			all immediate subcomponents are used (if the other subcomponent
			selection parameters, for example, `level`, are null. otherwise, the
			subcomponent selection is done by the Component's `disaggregate()`
			method
		level : int ( = 0 )
			the level of subcomponents to include in the calculation
		method : str ( = 'difa%' )
			the growth rate calculation of the aggregate real level. see the
			Modifications class in edan/aggregates/modifications.py for details
		args : positional arguments
			arguments to pass to the `modify()` method of the aggregate's real level
		kwargs : keyword arguments
			arguments to pass to the `modify()` method of the aggregate's real level

		Returns
		-------
		contribution : pandas DataFrame
		"""
		return self.compute(subs, level, method, *args, **kwargs)

	def compute(
		self,
		subs: Union[list, str, bool] = '',
		level: int = 0,
		method: Union[str, Callable] = '',
		*args, **kwargs
	):
		if self.obj.elemental:
			# if component has no subcomponent, return pandas Series of ones
			return pd.Series(
				data=np.ones(len(self.obj.real.data)),
				index=self.obj.real.data.index,
				name=self.obj.code
			)

		# compute the aggregate growth rate
		agg_growth = self.obj.real.modify(method, *args, **kwargs)

		# select the subcomponents whose contributions will be calculated
		self.subs = self.obj.disaggregate(subs, level)
		self.comps = [self.obj] + list(self.subs)

		# set `self.real` & `self.nominal` attributes, and indicators of ctypes
		self._set_ctypes_and_data()

		# compute the shares for all the flow and stock components, then aggregate
		#	the ones that are subcomponents of balance components
		shares_bal = self._calculate_shares()
		shares = self._compute_balances(shares_bal)

		# let pandas handle index-matching again
		growth = agg_growth.loc[self.real.index]
		contrs = np.multiply(shares, growth.values[:, None])

		return pd.DataFrame(
			contrs,
			index=growth.index,
			columns=self.codes
		)


	def _set_ctypes_and_data(self):
		"""
		set `self.real` & `self.nominal` attributes of the real and nominal data
		of both the aggregate & all the chosen subcomponents, and indicators of
		the ctypes of all components in `self.flows`, `self.balances`, and
		`self.stocks` attributes
		"""

		# real & nominal data, and series codes for renaming final dataframe.
		#	`less` is an indicator for components that should be subtracted
		#	from the agg
		rdata, ndata, self.codes, self.less = [], [], [], []

		# column indices of different Component types
		stocks = []
		flows = []
		def add_idx(comp, idx):
			if isinstance(comp, FlowComponent):
				flows.append(idx)
			else:
				stocks.append(idx)

		# don't use enumerate b/c we don't know if components are Balance
		#	components beforehand
		idx = 0
		for comp in self.comps:

			self.codes.append(comp.code)

			if isinstance(comp, BalanceComponent):
				for sub in comp.disaggregate():
					self.less.append(sub.is_less(self.obj.code))

					# i don't think there is ever a case where a BalanceComp
					#	will have a Balance sub but a check here could be good
					rdata.append(sub.real.data)
					ndata.append(sub.nominal.data)

					add_idx(sub, idx)
					idx += 1

			else:
				self.less.append(comp.is_less(self.obj.code))

				if isinstance(comp, FlowComponent):
					rdata.append(comp.real_level.data)
					ndata.append(comp.nominal_level.data)
				else:
					rdata.append(comp.real.data)
					ndata.append(comp.nominal.data)

				add_idx(comp, idx)
				idx += 1

		# let pandas handle joining & nans
		data = pd.concat(rdata + ndata, axis='columns').dropna(axis='index')

		# re-partition data; each block has the agg. series in the first col
		n_series = len(rdata)
		self.real = data.iloc[:, :n_series].round(1)
		self.nominal = data.iloc[:, n_series:].round(1)

		# construct indicator arrays for ctype now that BalanceComp locs are known
		self.stocks = np.zeros(n_series, dtype=bool)
		self.stocks[stocks] = True

		self.flows = np.zeros(n_series, dtype=bool)
		self.flows[flows] = True

	def _calculate_shares(self):
		"""
		calculate the contribution shares of subcomponents that are not
		BalanceComponents the calculation for the contribution shares is described
		in the footnotes of this table:
			https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

		that table is referenced in this old article from the BEA, along with
		some discussion about other new (in 1995) measures:
			https://apps.bea.gov/scb/account_articles/national/0795od/maintext.htm
		"""

		real, nominal = self.real.values, self.nominal.values

		# change in real level of component
		real_chg = np.empty(real.shape)
		real_chg[:] = np.nan

		real_chg[1:, self.stocks] = real[1:, self.stocks] - real[:-1, self.stocks]
		real_chg[2:, self.flows] = (real[2:, self.flows] - real[1:-1, self.flows]) - \
			(real[1:-1, self.flows] - real[:-2, self.flows])

		# price deflator implied by real & nominal levels
		deflator = np.empty(real.shape)
		deflator[:] = np.nan
		deflator[1:, :] = np.true_divide(nominal[:-1, :], real[:-1, :])

		# nominal level change
		nom_chg = np.multiply(deflator, real_chg)

		# fraction of change attributable to each component (first col is agg.)
		shares = np.empty(self.real.shape)
		shares[:] = np.nan
		shares[:, 0] = 1
		shares[:, 1:] = np.true_divide(nom_chg[:, 1:], nom_chg[:, :1])

		# account for any subtractions
		shares[:, self.less] = - shares[:, self.less]

		return shares

	def _compute_balances(self, shares_bal):
		"""
		after all the shares have been computed, we need to add/subtract the
		subcomponents of the BalanceComponents
		"""
		if any(isinstance(comp, BalanceComponent) for comp in self.comps):
			n_comps = len(self.comps)

			shares = np.empty((shares_bal.shape[0], n_comps))
			shares[:] = np.nan

			bal_idx = 0
			for idx, comp in enumerate(self.comps):

				if isinstance(comp, BalanceComponent):

					subs = comp.disaggregate()
					sub_contrs = np.zeros((shares.shape[0], len(subs)))

					for i, sub in enumerate(subs):
						sub_contrs[:, i] = shares_bal[:, bal_idx]
						bal_idx += 1

					shares[:, idx] = np.sum(sub_contrs, axis=1)

				else:
					shares[:, idx] = shares_bal[:, bal_idx]
					bal_idx += 1

			return shares

		else:
			return shares_bal


class Share(Feature):
	"""
	the fraction of the real/nominal level attributable to each subcomponent.
	that same ratio for quantity/price indices really don't make sense economically,
	but no checks are made when it comes to those mtypes
	"""
	name = 'share'

	def __call__(
		self,
		subs: Union[list, str, bool] = '',
		level: int = 0,
		mtype: str = 'nominal'
	):
		"""
		compute and return the ratio of {agg mtype}/{sub mtype} for all the chosen
		subcomponents. the first column of the returned dataframe is just ones.

		Parameters
		----------
		subs : list | str ( = '' )
			the subcomponents to include in the calculation. if an empty string,
			all immediate subcomponents are used (if the other subcomponent
			selection parameters, for example, `level`, are null. otherwise, the
			subcomponent selection is done by the Component's `disaggregate()`
			method
		level : int ( = 0 )
			the level of subcomponents to include in the calculation
		mtype : str ( = 'nominal' )
			the mtype of the components to compute the ratio of. the ratio of the
			quantity/price indices don't really make sense economically, but no
			checks are made to prevent it

		Returns
		-------
		share : pandas DataFrame
		"""
		return self.compute(subs, level, mtype)

	def compute(
		self,
		subs: Union[list, str, bool] = '',
		level: int = 0,
		mtype: str = 'nominal'
	):
		if self.obj.elemental:
			# if component has no subcomponent, return Series of ones
			return pd.Series(
				data=np.ones(len(self.obj.nominal.data)),
				index=self.obj.nominal.data.index,
				name=self.obj.code
			)

		# select the subcomponents
		self.subs = self.obj.disaggregate(subs, level)
		self.comps = [self.obj] + list(self.subs)

		# collect data based on mtype
		frames, self.codes  = [], []
		for comp in self.comps:
			series = getattr(comp, mtype)

			frames.append(series.data)
			self.codes.append(comp.code)
		data = pd.concat(frames, axis='columns').dropna(axis='index', how='all')

		# after pandas handles matching periods & nans, calculate shares
		shares = np.empty(data.shape)
		shares[:] = np.nan

		shares[:, 0] = np.ones(shares.shape[0])
		shares[:, 1:] = np.true_divide(data.iloc[:, 1:].values, data.iloc[:, :1].values)

		return pd.DataFrame(
			shares,
			index=data.index,
			columns=self.codes
		)




def contributions(
	obj,
	subs: Union[list, str, bool] = '',
	level: int = 0,
	method: Union[str, Callable] = '',
	*args, **kwargs
):
	"""
	compute & return a dataframe of subcomponents' contributions to percent
	change of an aggregate. the calculations are described in the footnotes
	of this table:
		https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

	by default, the contribution from all direct subcomponents are computed,
	but this can be changed via the `subs` and `level` parameters

	Parameters
	----------
	subs : list | str ( = '' )
		the subcomponents to include in the calculation. if an empty string,
		all immediate subcomponents are used (if the other subcomponent
		selection parameters, for example, `level`, are null. otherwise, the
		subcomponent selection is done by the Component's `disaggregate()`
		method
	level : int ( = 0 )
		the level of subcomponents to include in the calculation
	method : str ( = 'difa%' )
		the growth rate calculation of the aggregate real level. see the
		Modifications class in edan/aggregates/modifications.py for details
	args : positional arguments
		arguments to pass to the `modify()` method of the aggregate's real level
	kwargs : keyword arguments
		arguments to pass to the `modify()` method of the aggregate's real level

	Returns
	-------
	contribution : pandas DataFrame
	"""
	contr = Contribution(obj)
	return contr.compute(subs, level, method, *args, **kwargs)


def shares(
	obj,
	subs: Union[list, str, bool] = '',
	level: int = 0,
	mtype: str = 'nominal'
):

	"""
	compute and return the ratio of {agg mtype}/{sub mtype} for all the chosen
	subcomponents. the first column of the returned dataframe is just ones.

	Parameters
	----------
	subs : list | str ( = '' )
		the subcomponents to include in the calculation. if an empty string,
		all immediate subcomponents are used (if the other subcomponent
		selection parameters, for example, `level`, are null. otherwise, the
		subcomponent selection is done by the Component's `disaggregate()`
		method
	level : int ( = 0 )
		the level of subcomponents to include in the calculation
	mtype : str ( = 'nominal' )
		the mtype of the components to compute the ratio of. the ratio of the
		quantity/price indices don't really make sense economically, but no
		checks are made to prevent it

	Returns
	-------
	share : pandas DataFrame
	"""
	shr = Share(obj)
	return shr.compute(subs, level, mtype)
