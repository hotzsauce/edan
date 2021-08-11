"""
aggregating NIPA components
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.nipa.core import NIPAComponent, NIPASeries
from edan.core.components import FlowComponent, BalanceComponent



from rich import print


def aggregate_nipa(
	objs: Iterable[NIPAComponent],
	code: str = '',
	level: int = 0,
	long_name: str = '',
	short_name: str = '',
	table: str = ''
):
	"""
	aggregate a collection of NIPAComponents into a 'synthetic' NIPA component.
	at the moment, FlowComponents and BalanceComponents are not handled, and
	will throw a NotImplementedError if one is included in `objs`

	Parameters
	----------
	objs : Iterable[Component]
		the collection of Components to aggregate
	code : str ( = '' )
		the code of the synthetic component
	level : str ( = 0 )
		the level of the synthetic component
	long_name : str ( = '' )
		the string assigned to the `long_name` attribute of the component
	short_name : str ( = '' )
		the string assigned to the `short_name` attribute of the component
	table : str ( = '' )
		the NIPA table that all `objs` belong to. this check is done by the
		top-level `aggregate` function

	Returns
	-------
	Component
	"""
	source = 'bea'

	# gather data
	if any(isinstance(o, (FlowComponent, BalanceComponent)) for o in objs):
		raise NotImplementedError("cannot aggregate Flow- or BalanceComponents now")

	# nominal level is just sum of sub-components
	nom_frames = [comp.nominal.data for comp in objs]
	nom_data = pd.concat(nom_frames, axis='columns').dropna(axis='index', how='all')
	nominal = nom_data.sum(axis='columns')

	# use chain-weighting to compute the real level, then compute implied price
	#	and quantity indices
	real = compute_real_level(objs)
	price = 100 * (nominal / real)
	quant = compute_quantity_index(nominal, price)

	# we excluded FlowComponents above, so, for the moment we don't need to deal
	#	with `real_level` or `nominal_level` mtypes
	codes = {
		'quantity': 'q' + code, 'price': 'p' + code,
		'nominal': 'n' + code, 'real': 'r' + code
	}

	agg_comp = NIPAComponent(
		code=code,
		level=level,
		long_name=long_name,
		short_name=short_name,
		source=source,
		table=table,
		**codes
	)
	agg_comp.subs = objs

	def _series(c, m, d):
		return NIPASeries(code=c+code, mtype=m, data=d, comp=agg_comp)

	agg_comp.quantity = _series('q', 'quantity', quant)
	agg_comp.price = _series('p', 'price', price)
	agg_comp.nominal = _series('n', 'nominal', nominal)
	agg_comp.real = _series('r', 'real', real)

	return agg_comp



def compute_real_level(objs: Iterable[NIPAComponent]):
	chain = ChainWeighter(objs)
	return chain.compute()


class ChainWeighter(object):

	def __init__(self, objs):

		# subcomponents that will be used to create aggregate level
		self.objs = objs

	def compute(self):

		# set `self.real` & `self.price` attributes, and indicators of ctypes
		self._set_ctypes_and_data()

		# chained-weight indices of the selected subcomponents
		self.weights = self._compute_chained_weights()

		# after weights are computed, use them to find the whole chain series
		return self._chain()


	def _set_ctypes_and_data(self):
		"""
		set `self.real` and `self.price` attributes of the real level and price
		index data of all the chosen components, and indicators of the ctypes
		of all components in `self.flows`, `self.balances`, and `self.stocks`
		"""

		# real & price data, and series codes for renaming final dataframe.
		#	`less` is an indicator for components that should be subtracted
		#	from the aggregate
		rdata, pdata, self.codes, self.less = [], [], [], []

		# column indices of different Component types
		stocks, flows = [], []
		def add_idx(comp, idx):
			if isinstance(comp, FlowComponent):
				flows.append(idx)
			else:
				stocks.append(idx)

		# don't use enumerate b/c we don't know if components are Balance
		#	components beforehand
		idx = 0
		for comp in self.objs:

			self.codes.append(comp.code)

			if isinstance(comp, BalanceComponent):
				for sub in comp.disaggregate():
					self.less.append(sub.is_less())

					# i don't think there is ever a case where a BalanceComponent
					#	will have a Balance sub but a check here could be good
					rdata.append(sub.real.data)
					pdata.append(sub.price.data)

					add_idx(sub, idx)
					idx += 1

			else:
				self.less.append(comp.is_less())

				rdata.append(comp.real.data)
				pdata.append(comp.price.data)

				add_idx(comp, idx)
				idx += 1

		# let pandas handle joining & nans
		data = pd.concat(rdata + pdata, axis='columns').dropna(axis='index')

		# re-partition data
		n_series = len(rdata)
		self.real = data.iloc[:, :n_series]
		self.price = data.iloc[:, n_series:]

		# construct indicator arrays for ctype now that BalanceComp locs are known
		self.stocks = np.zeros(n_series, dtype=bool)
		self.stocks[stocks] = True

		self.flows = np.zeros(n_series, dtype=bool)
		self.flows[flows] = True

	def _compute_chained_weights(self):
		real, price = self.real.values, self.price.values

		# time period t & time period t-1 of quantity & prices
		qt_pt = np.sum(np.multiply(real[1:, :], price[1:, :]), axis=1)
		qt_ptm1 = np.sum(np.multiply(real[1:, :], price[:-1, :]), axis=1)
		qtm1_pt = np.sum(np.multiply(real[:-1, :], price[1:, :]), axis=1)
		qtm1_ptm1 = np.sum(np.multiply(real[:-1, :], price[:-1, :]), axis=1)

		# shoutout to the germans
		paasche = np.true_divide(qt_pt, qtm1_pt)
		laspeyres = np.true_divide(qt_ptm1, qtm1_ptm1)

		# pre-allocate chain weights
		weights = np.empty(real.shape[0])
		weights[:] = 1.0
		weights[1:] = np.sqrt(np.multiply(paasche, laspeyres))

		return weights

	def _chain(self):

		weights = self.weights

		# base year for both GDP and PCE real series is 2012
		base_year = 2012
		base_locs = self.real.index.year == base_year

		# the real level of the base year is the average of the aggregate level.
		#	we sum the normally non-additive real level because, in the base year
		#	only, avg(nominal level) = average(real level)
		base_data = self.real.loc[base_locs].to_numpy()
		real_base = np.mean(np.sum(base_data, axis=1))

		# chain weights together & find their average in the base year
		weight_path = np.cumprod(weights)
		weight_base = np.mean(weight_path[base_locs])

		real = weight_path * (real_base/weight_base)

		return pd.Series(
			real,
			index=self.real.index
		)



def compute_quantity_index(nominal: pd.Series, price: pd.Series):

	# base year for both GDP and PCE real series is 2012
	base_year = 2012

	# changes in nominal/price ratio are identical to quantity changes
	nom_price = nominal / price
	np_changes = nom_price / nom_price.shift()

	# compute the quantity index from the price changes
	quant = np.empty(nominal.shape[0])
	quant[0] = 100
	quant[1:] = 100 * np.cumprod(np_changes.values[1:])

	# normalize to base period
	base_locs = nominal.index.year == base_year
	quant = 100 * np.true_divide(quant, np.mean(quant[base_locs]))

	return pd.Series(quant, index=nominal.index)
