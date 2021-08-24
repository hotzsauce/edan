"""
module for computing features of NIPA data. 'features' are distinct from the
'transformations' in `edan.core.transformations` because features involve
more than growth rates or moving averages of a single series - sometimes they
even might involve data from other related NIPA components
"""

from __future__ import annotations
from functools import cached_property

import pandas as pd
import numpy as np


from edan.core.components import (
	FlowComponent,
	BalanceComponent
)

from edan.core.transformations import (
	Feature,
	transform
)



class _Contribution(object):
	"""
	calculates the percent contribution to real change or percent contribution
	to inflation of subcomponents to the same change of the aggregate
	"""

	mtype = ''

	def __init__(self, agg, subs, level):
		self.agg = agg
		self._subs = subs
		self._level = level

		# set `flow`, `bals`, `stocks` indicator series for the various kinds
		#	of Component types (calculations vary by ctype) and create a list
		#	of the NIPASeries objects
		self._subcomponents = self._gather_subs_collect_ctypes()

	@cached_property
	def subs(self):
		return self.agg.disaggregate(self._subs, self._level)

	@cached_property
	def comps(self):
		return [self.agg] + list(self.subs)

	@property
	def codes(self):
		return [c.code for c in self.comps]

	def _gather_subs_collect_ctypes(self):
		"""

		"""
		# list of Flow, Stock, and subs of Balance components
		components = []

		# indicators for Flow and Stock components, and subcomponents of Balance
		#	components. in this last indicator array, '+1' refers to a sub that
		#	contributes positively to the Balance, '-1' negatively so, and '0'
		#	means that Component is either Flow or Stock
		flows, stocks, bals = [], [], []

		def add_idx(comp, idx, relative=None):
			if isinstance(comp, FlowComponent):
				flows.append(idx)
			else:
				stocks.append(idx)

		def add_bal(comp, non_less):
			if comp.is_less(self.agg.code):
				bals.append(-1)
			else:
				bals.append(non_less)

		# don't use enumerate b/c we don't know which comps are Balance beforehand
		idx = 0
		for comp in self.comps:

			if isinstance(comp, BalanceComponent):
				for sub in comp.disaggregate():
					add_idx(sub, idx)
					add_bal(sub, 1)

					components.append(sub)
					idx += 1

			else:
				add_idx(comp, idx)
				add_bal(comp, 0)

				components.append(comp)
				idx += 1

		# construct indicator arrays for ctype now that BalanceComponent
		#	locations are known
		n_series = len(components)
		self.stocks = np.zeros(n_series, dtype=bool)
		self.stocks[stocks] = True

		self.flows = np.zeros(n_series, dtype=bool)
		self.flows[flows] = True

		# balance indicators from list to np.ndarray
		self.bals = np.array(bals, dtype=int)
		return components

	def _data(self, mtype, flow_type=None):
		"""
		retrieve data of the input subcomponents of the desired `mtype`
		"""

		_flow_type = mtype+'_level' if flow_type == None else flow_type
		def _get_data(comp):
			if isinstance(comp, FlowComponent):
				series_obj = getattr(comp, _flow_type)
			else:
				series_obj = getattr(comp, mtype)
			return series_obj.data

		frames = [_get_data(comp) for comp in self._subcomponents]
		return pd.concat(frames, axis='columns').dropna(axis='index', how='all')

	def _apply_balances(self, arr, aggr=None):
		"""
		aggregate the additive and subtractive subcomponents of Balance
		subcomponents.

		Parameters
		----------
		arr : numpy ndarray
			an array with len(self.bals) columns that corresponds to the data of
			subcomponents
		aggr : callable ( = None )
			an aggregating method that accepts one parameter: the additive and
			subtractive data for a single balance component. if not provided,
			the data are simply added together using np.nansum, with `axis=1`

		Returns
		-------
		balanced : numpy ndarray
			an array with shape (arr.shape[0], len(stock & balance components).
			the columns corresponding to stock variables are unchanged from the
			analagous columns in `arr`. the balance-related columns are aggregated
			using `aggr`
		"""

		if np.all(self.bals == 0):
			return arr

		if aggr == None:
			aggr = lambda x: np.sum(x, axis=1)

		# indexes of stock and balance components in the input `arr` and the
		#	eventual, aggregated array
		outs, outb, ins, inb = _create_stock_balance_indices(self.bals)
		bal_grps = _create_balance_groups(self.bals)

		# pre-allocate output array & immediately fill the stock data
		output = np.zeros((arr.shape[0], len(outs)+len(outb)), dtype=float)
		output[:, outs] = arr[:, ins]

		# aggregate each of the groups
		for ob, grp in zip(outb, bal_grps):
			output[:, ob] = aggr(arr[:, grp[0]:grp[1]])

		return output



class _RealContribution(_Contribution):
	"""
	calculates the percent contribution to real change of subcomponents with respect
	to the change in the aggregate
	"""

	mtype = 'real'

	def compute(self, method, *args, **kwargs):
		if self.agg.elemental:
			# if component has no subcomponent, return pandas Series of ones
			real_series = self.agg.real.data
			return pd.Series(
				data=np.ones(len(real_series)),
				index=real_series.index,
				name=self.agg.code
			)

		# compute the aggregate growth rate
		agg_growth = self.agg.real.transform(method, *args, **kwargs)

		# compute shares and their contribution rates
		shares = self.shares
		contrs = np.multiply(shares, agg_growth.to_numpy()[:, np.newaxis])

		return pd.DataFrame(
			contrs,
			index=agg_growth.index,
			columns=self.codes
		)

	@property
	def shares(self):
		"""
		calculate the contribution shares of subcomponents that are not
		BalanceComponents the calculation for the contribution shares is described
		in the footnotes of this table:
			https://apps.bea.gov/scb/account_articles/national/0795od/table1.htm

		that table is referenced in this old article from the BEA, along with
		some discussion about other new (in 1995) measures:
			https://apps.bea.gov/scb/account_articles/national/0795od/maintext.htm
		"""

		# collect real and nominal data into numpy arrays, and set various indicators
		rdf, ndf = self._data('real'), self._data('nominal')
		real, nominal = rdf.values, ndf.values

		# change in real level of component
		real_chg = np.full(real.shape, np.nan)
		real_chg[1:, self.stocks] = real[1:, self.stocks] - real[:-1, self.stocks]
		real_chg[2:, self.flows] = (real[2:, self.flows] - real[1:-1, self.flows]) - \
			(real[1:-1, self.flows] - real[:-2, self.flows])

		# price deflator implied by real & nominal levels
		deflator = np.full(real.shape, np.nan)
		deflator[1:, :] = np.true_divide(nominal[:-1, :], real[:-1, :])

		# nomiinal level change. we will eventually divide by `nom_chg`, so to suppress
		#	numpy RuntimeWarnings, we set any zeros to NaNs
		nom_chg = np.multiply(deflator, real_chg)
		nom_chg[nom_chg == 0] = np.nan

		# fraction of change attributable to each component (first column is agg.)
		shares = np.full(rdf.shape, np.nan)
		shares[:, 0] = 1
		shares[:, 1:] = np.true_divide(nom_chg[:, 1:], nom_chg[:, :1])

		# if any of the nominal changes were NaN, set their share to zero
		shares[np.isnan(shares)] = 0

		# reverse sign of subtractive Balance subs, then aggregate
		shares[:, self.bals == -1] = -shares[:, self.bals == -1]
		balanced = self._apply_balances(shares)
		return balanced



class _PriceContribution(_Contribution):
	"""
	calculates the percent contribution to inflation of subcomponents with respect
	to the change in the aggregate
	"""

	mtype = 'price'

	def compute(self, method, *args, **kwargs):
		if self.agg.elemental:
			# if component has no subcomponent, return pandas Series of ones
			return pd.Series(
				data=np.ones(len(self.agg.price.data)),
				index=self.agg.price.data.index,
				name=self.obj.code
			)

		# weight subcomponents' inflation rates by their nominal shares, and access
		#	the price indices
		rates = self.weighted_inflation
		init_price = self.initial_price_index

		# the first row of `rates` is just nan. replace them with ones, then create a
		#	contribution-aware rate path
		rates[0, :] = 1
		rpath = np.cumprod(1 + rates / 100, axis=0)

		# add datetime index and codes
		prices = np.multiply(rpath, init_price)
		contr_df = pd.DataFrame(
			prices,
			index=self.agg.price.data.index,
			columns=self.codes
		)
		return transform(contr_df, method, *args, **kwargs)

	@property
	def weighted_inflation(self):
		"""
		calculate the weighted inflation rates of the aggregate (not actually
		weighted) and the subcomponents
		"""

		# collect price and nominal data into numpy arrays, and set various indicators
		# pdf, ndf = self._gather_data_set_ctypes()
		pdf, ndf = self._data('price'), self._data('nominal')
		price, nominal = pdf.to_numpy(), ndf.to_numpy()

		# period-to-period inflation & nominal shares
		infl = 100 * (np.true_divide(price[1:], price[:-1]) - 1)
		nom_shares = np.true_divide(nominal[1:], nominal[1:, 0][:, np.newaxis])

		# weight the inflation rates by their nominal shares of the aggregate
		weighted = np.multiply(infl, nom_shares)

		# reverse sign of any subcomponents of BalanceComponents that need to be
		#	subtracted, then compute the BalanceComp's contribution
		weighted[:, self.bals == -1] = -weighted[:, self.bals == -1]

		# for consistency with other _Contribution subclasses, add a row for the
		#	first period. then add growth rates according to Balance sub locs
		weighted = np.insert(weighted, 0, np.nan, axis=0)
		return self._apply_balances(weighted)

	@property
	def initial_price_index(self):
		"""
		the inital price index values are partitioned into two groups:
			1) stock components. the initial values are just the subcomponent's
				first price index observation
			2) balance components. the initial values are the weighted sum of the
				price indices of the subcomponents of the Balance component, with
				the weight of the j-th subcomponent being equal to
					nominal_j / sum(nominal)
		"""
		outs, outb, ins, inb = _create_stock_balance_indices(self.bals)
		bal_grps = _create_balance_groups(self.bals)

		# get the first observation of nominal level and price indices
		nom = self._data('nominal').to_numpy()[0, :]
		price = self._data('price').to_numpy()[0, :]

		# preallocate output array
		init = np.zeros(len(outs) + len(outb), dtype=float)
		init[outs] = price[ins]
		for ob, grp in zip(outb, bal_grps):

			nom_grp = nom[grp[0]:grp[1]]
			price_grp = price[grp[0]:grp[1]]

			init[ob] = np.dot(nom_grp, price_grp) / np.sum(nom_grp)

		return init



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
		mtype: str = 'real',
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
		mtype : str ( = 'real' )
			the mtype of contributions to compute. only 'real' and 'price' are
			accepted
		method : str ( = '' )
			the growth rate calculation of aggregate growth. if `mtype = 'real'`,
			default is 'difa%', and if `mtype = 'price'`, the default value of
			`method` is 'yryr%'. see the TransformationAccessor class in
			edan/core/transformations.py for details
		args : positional arguments
			arguments to pass to the `transform()` method of the aggregate's real level
		kwargs : keyword arguments
			arguments to pass to the `transform()` method of the aggregate's real level

		Returns
		-------
		contribution : pandas DataFrame
		"""

		if mtype == 'real':
			_contr = _RealContribution(self.obj, subs, level)
			if method == '':
				method = 'difa%'

		elif mtype == 'price':
			_contr = _PriceContribution(self.obj, subs, level)
			if method == '':
				method = 'yryr%'

		else:
			if isinstance(mtype, str):
				raise ValueError(f"cannot compute contributions of mtype '{mtype}'")
			else:
				raise TypeError("'mtype' must be a string")

		return _contr.compute(method, *args, **kwargs)



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
		compute and return the ratio of {sub mtype}/{agg mtype} for all the chosen
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
	mtype: str = 'real',
	method: Union[str, Callable] = 'difa%',
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
	mtype : str ( = 'real' )
		the mtype of contributions to compute. only 'real' and 'price' are
		accepted
	method : str ( = 'difa%' )
		the growth rate calculation of the aggregate real level. see the
		TransformationAccessor class in edan.core.transformations.py
		for details
	args : positional arguments
		arguments to pass to the `transform()` method of the aggregate's real level
	kwargs : keyword arguments
		arguments to pass to the `transform()` method of the aggregate's real level

	Returns
	-------
	contribution : pandas DataFrame
	"""
	contr = Contribution(obj)
	return contr(subs, level, mtype, method, *args, **kwargs)


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


"""
a couple methods for dealing with the locations of the subcomponents of Balance
components in arrays of those sub's data.
"""
def _create_stock_balance_indices(bal):
	"""
	from an array of indicators recording the location of Stock components
	(denoted by a zero), additive subs of Balance comps (denoted by a positive
	one), and subtractive subs of Balance comps (a negative one), calculate the
	index locations of Stock components and the first additive Balance sub.
		these index locations are computed both in terms of the input data,
	and the output data, which will merge the additive and subtractive
	subcomponents in some way (usually just simple adding)
	"""

	# balance and stock indices in the input data
	bal_offset = np.hstack((0, bal[:-1]))
	in_bal = np.flatnonzero(np.logical_and(bal == 1, bal_offset != 1))
	in_stock = np.flatnonzero(bal == 0)

	# combine the two input indices (sort in place to avoid copies)
	all_outs = np.concatenate((in_stock, in_bal))
	all_outs.sort()

	# find locations of the stock and balance components in output array
	out_bal = np.searchsorted(all_outs, in_bal)
	out_stock = np.searchsorted(all_outs, in_stock)

	return out_stock, out_bal, in_stock, in_bal


def _create_balance_groups(bal):
	"""
	from an array of indicators recording the location of Stock components
	(denoted by a zero), additive subs of Balance comps (denoted by a positive
	one), and subtractive subs of Balance comps (a negative one), record the
	locations of the additive and subtractive subcomponents.
		specifically, a list of tuples of indices is returned. each tuple has
	two elements: the first element of the n-th tuple is the index of the n-th
	leading-additive subcomponent, and the second element is the index of the
	last subcomponent of the n-th balance component
	"""
	outs, outb, ins, inb = _create_stock_balance_indices(bal)

	# combine the two input indices & sort. add a ceiling element in case the
	#	last output component is a balance component
	in_indices = np.hstack((ins, inb, len(bal)))
	in_indices.sort()

	# find the right-border indices of the boundary groups. the left-border indices
	#	is `inb`; the location of the first positive sub of balance components
	blk = np.tile(in_indices, (len(inb), 1)).transpose()
	rborders = np.amin(np.where(blk-inb>0, blk, np.inf), axis=0).astype(int)

	borders = np.vstack((inb, rborders))
	return [tuple(borders[:, i]) for i in range(len(inb))]
