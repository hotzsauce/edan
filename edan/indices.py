"""
module for computing quantity and price indices
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from edan.core.base import BaseComponent

from rich import print


__all__ = [
	'paasche',
	'laspeyres',
	'fisher',
	'tornqvist',
	'walsh',
	'geometric',
	'marshall_edgeworth',
	'carli',
	'dutot',
	'jevons',
	'harmonic_mean',
	'cswd_index',
	'harmonic_ratios'
]


# front-facing methods
def paasche(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Paasche index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Paasche price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Paasche price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Paasche price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Paasche index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	paasche
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _PaascheIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



def laspeyres(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Laspeyres index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Laspeyres price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Laspeyres price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Laspeyres price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Laspeyres index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	laspeyres
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _LaspeyresIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



def fisher(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Fisher index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Fisher price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Fisher price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Fisher price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Fisher index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	fisher
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _FisherIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



def tornqvist(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Tornqvist index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Tornqvist price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Tornqvist price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Tornqvist price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Tornqvist index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not. the Tornqvist
		index is chained definitionally, so this is here to maintain consistency across
		function signatures.
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	tornqvist
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _TornqvistIndexConstructor(price, quantity, mtype)
	return _idx.compute(base=base)



def walsh(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Walsh index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Walsh price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Walsh price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Walsh price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Walsh index to compute. accepted values are 'price' and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	walsh
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _WalshIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



def geometric(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the geometric index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		geometric price or quantity index. this parameter can be given either as
		a positional or keyword argument, but in either case, if `quantity` or
		`price` are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new geometric price or quantity index. this
		can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new geometric price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `price`
		parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of geometric index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	geometric
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _GeometricIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



def marshall_edgeworth(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
) -> pd.Series:
	"""
	compute the Marshall-Edgeworth index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new
		Marshall-Edgeworth price or quantity index. this parameter can be given either
		as a positional or keyword argument, but in either case, if `quantity` or `price`
		are also passed, a ValueError is raised
	price : pandas DataFrame | pandas Series ( = None )
		the price data used to create a new Marshall-Edgeworth price or quantity index.
		this can only be passed as a keyword, and must be accompanied by a `quantity`
		parameter as well. if `objs` is also provided, a ValueError is raised
	quantity : pandas DataFrame | pandas Series ( = None )
		the quantity data used to create a new Marshall-Edgeworth price or quantity
		index. this can only be passed as a keyword, and must be accompanied by a
		`price` parameter as well. if `objs` is also provided, a ValueError is raised
	mtype : str ( = 'price' )
		the type of Marshall-Edgeworth index to compute. accepted values are 'price'
		and 'quantity'
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	price_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the
		price data in the calculation
	quantity_mtype : str ( = 'real' )
		if `objs` is provided, this is the name of the mtype to use for the
		quantity data in the calculation

	Returns
	-------
	marshall_edgeworth
		pandas Series
	"""

	price, quantity = _gather_index_data(
		objs=objs,
		price=price,
		quantity=quantity,
		price_mtype=price_mtype,
		quantity_mtype=quantity_mtype
	)

	_idx = _MarshallEdgeworthIndexConstructor(price, quantity, mtype)
	return _idx.compute(chained=chained, base=base)



# front-facing univariate, unweighted indices
def carli(
	objs: Iterable[Component] = None,
	data: Union[DataFrame, Series] = None,
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the Carli index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new Carli price
		or quantity index. this parameter can be given either as a positional or keyword
		argument, but in either case, if `data` is also passed, a ValueError is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new Carli price or quantity index. this can only be
		passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	carli
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _CarliIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)



def dutot(
	objs: Iterable[Component] = None,
	data: Union[DataFrame, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the Dutot index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new Dutot price
		or quantity index. this parameter can be given either as a positional or keyword
		argument, but in either case, if `data` is also passed, a ValueError is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new Dutot price or quantity index. this can only be
		passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	dutot
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _DutotIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)



def jevons(
	objs: Iterable[Component] = None,
	data: Union[Dataframe, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the Jevons index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new Jevons price
		or quantity index. this parameter can be given either as a positional or keyword
		argument, but in either case, if `data` is also passed, a ValueError is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new Jevons price or quantity index. this can only be
		passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	jevons
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _JevonsIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)



def harmonic_mean(
	objs: Iterable[Component] = None,
	data: Union[Dataframe, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the harmonic mean index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new harmonic mean
		price or quantity index. this parameter can be given either as a positional or
		keyword argument, but in either case, if `data` is also passed, a ValueError
		is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new harmonic mean price or quantity index. this can
		only be passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	harmonic_mean
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _HarmonicMeanIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)



def cswd_index(
	objs: Iterable[Component] = None,
	data: Union[Dataframe, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the Carruthers, Sellwood, Word, Dalen index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new CSWD price
		quantity index. this parameter can be given either as a positional or keyword
		argument, but in either case, if `data` is also passed, a ValueError
		is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new CSWD price or quantity index. this can only be
		passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	harmonic_mean
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _CSWDIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)



def harmonic_ratios(
	objs: Iterable[Component] = None,
	data: Union[Dataframe, Series] = None,
	mtype: str = 'price',
	chained: bool = True,
	base: Union[int, str, Timestamp] = 2012,
	obj_mtype: str = 'price'
) -> pd.Series:
	"""
	compute the harmonic ratio index for a basket of Components

	Parameters
	----------
	objs : iterable of Components ( = None )
		a collection of Components whose data will be used to create a new harmonic
		ratio price or quantity index. this parameter can be given either as a positional
		or keyword argument, but in either case, if `data` is also passed, a ValueError
		is raised
	data : pandas DataFrame | pandas Series ( = None )
		the data used to create a new harmonic ratio  price or quantity index. this can
		only be passed as a keyword. if `objs` is also provided, a ValueError is raised
	chained : bool ( = True )
		indicator of whether to create a chained index series or not
	base : int | datetime-like ( = 2012 )
		the base period of the output index
	obj_mtype : str ( = 'price' )
		if `objs` is provided, this is the name of the mtype to use for the data in the
		calculation

	Returns
	-------
	harmonic_ratio
		pandas Series
	"""

	data = _gather_unweighted_index_data(
		objs=objs,
		data=data,
		obj_mtype=obj_mtype
	)

	_idx = _HarmonicRatioIndexConstructor(data)
	return _idx.compute(chained=chained, base=base)




# classes & method that do the actual computation of index construction
def _gather_index_data(
	objs: Iterable[Component] = None,
	price: Union[DataFrame, Series] = None,
	quantity: Union[DataFrame, Series] = None,
	price_mtype: str = 'price',
	quantity_mtype: str = 'real'
):
	if objs:
		if (price is not None) or (quantity is not None):
			raise ValueError(
				"'price' and 'quantity' parameters cannot be provided if 'objs' is"
			)

		price_frames, quantity_frames = [], []
		for obj in objs:
			if not isinstance(obj, BaseComponent):
				raise TypeError(f"{type(obj)}. all elements must be edan Components")

			price_frames.append(getattr(obj, price_mtype).data)
			quantity_frames.append(getattr(obj, quantity_mtype).data)

		price = pd.concat(price_frames, axis='columns')
		quantity = pd.concat(quantity_frames, axis='columns')

	else:
		if (price is None) or (quantity is None):
			raise ValueError(
				"'price' and 'quantity' parameters are required if 'objs' is not given"
			)

	return price, quantity



def _gather_unweighted_index_data(
	objs: Iterable[Component] = None,
	data: Union[DataFrame, Series] = None,
	obj_mtype: str = 'price',
):
	if objs:
		if data is not None:
			raise ValueError("'data' parameters cannot be provided if 'objs' is")

		frames = []
		for obj in objs:
			if not isinstance(obj, BaseComponent):
				raise TypeError(f"{type(obj)}. all elements must be edan Components")

			frames.append(getattr(obj, obj_mtype).data)

		data = pd.concat(frames, axis='columns')

	else:
		if data is None:
			raise ValueError("'data' parameters are required if 'objs' is not given")

	return data



class _IndexConstructor(object):

	def __init__(
		self,
		price: Union[Series, DataFrame],
		quantity: Union[Series, DataFrame],
		mtype: str
	):

		if mtype not in ('price', 'quantity'):
			if not isinstance(mtype, str):
				raise TypeError(f"{type(mtype)}. 'mtype' must be a string")
			raise ValueError("'mtype' must be one of 'price' or 'quantity'")

		if not isinstance(price, (pd.Series, pd.DataFrame)):
			raise TypeError(
				f"{type(price)}. 'price' must be pandas Series or DataFrame"
			)

		if not isinstance(quantity, (pd.Series, pd.DataFrame)):
			raise TypeError(
				f"{type(quantity)}. 'quantity' must be pandas Series or DataFrame"
			)

		# ensure the two objects have the same number of columns and rows
		ps = 1 if isinstance(price, pd.Series) else price.shape[1]
		qs = 1 if isinstance(quantity, pd.Series) else quantity.shape[1]
		if ps != qs:
			raise ValueError("'price' and 'quantity' have differing number of columns")

		if not price.index.equals(quantity.index):
			raise ValueError("'price' and 'quantity' do not have the same index")

		self.mtype = mtype
		# ensure price and quantity data are DataFrames, just so the subclasses
		#	don't have to have a series of checks
		try:
			self.price = price.to_frame()
		except AttributeError:
			self.price = price

		try:
			self.quantity = quantity.to_frame()
		except AttributeError:
			self.quantity = quantity



class _PaascheIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:

			pt, qt = parr[1:, :], qarr[1:, :]
			numer = np.sum(np.multiply(pt, qt), axis=1)

			if self.mtype == 'price':
				denom = np.sum(np.multiply(parr[:-1, :], qt), axis=1)

			elif self.mtype == 'quantity':
				denom = np.sum(np.multiply(pt, qarr[:-1, :]), axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			paasche = pd.Series(
				chain,
				index=self.price.index,
				name=f'paasche_{self.mtype}'
			)

			scale = rbase.compute_base_value(paasche)
			return 100 * (paasche / scale)

		else:
			pt, qt = parr, qarr
			numer = np.sum(np.multiply(pt, qt), axis=1)

			idx = rbase.locate_base_periods(self.price)
			if self.mtype == 'price':
				pb = np.mean(parr[idx, :], axis=0)
				denom = np.sum(np.multiply(pb, qt), axis=1)

			elif self.mtype == 'quantity':
				qb = np.mean(qarr[idx, :], axis=0)
				denom = np.sum(np.multiply(pt, qb), axis=1)

			return pd.Series(
				100 * np.true_divide(numer, denom),
				index=self.price.index,
				name=f'paasche_{self.mtype}'
			)



class _LaspeyresIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:

			ptm1, qtm1 = parr[:-1, :], qarr[:-1, :]
			denom = np.sum(np.multiply(ptm1, qtm1), axis=1)

			if self.mtype == 'price':
				numer = np.sum(np.multiply(parr[1:, :], qtm1), axis=1)

			elif self.mtype == 'quantity':
				numer = np.sum(np.multiply(ptm1, qarr[1:, :]), axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			laspeyres = pd.Series(
				chain,
				index=self.price.index,
				name=f'laspeyres_{self.mtype}'
			)

			scale = rbase.compute_base_value(laspeyres)
			return 100 * (laspeyres / scale)

		else:
			# locate price and quantity values in base period, average them in case
			#	the base period is an entire year
			idx = rbase.locate_base_periods(self.price)
			pb = np.mean(parr[idx, :], axis=0)
			qb = np.mean(qarr[idx, :], axis=0)

			denom = np.dot(pb, qb)

			if self.mtype == 'price':
				numer = np.sum(np.multiply(parr, qb), axis=1)

			elif self.mtype == 'quantity':
				numer = np.sum(np.multiply(pb, qarr), axis=1)

			return pd.Series(
				100 * np.true_divide(numer, denom),
				index=self.price.index,
				name=f'laspeyres_{self.mtype}'
			)



class _FisherIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:

			pt, qt = parr[1:, :], qarr[1:, :]
			ptm1, qtm1 = parr[:-1, :], qarr[:-1, :]

			pt_qt = np.sum(np.multiply(pt, qt), axis=1)
			ptm1_qt = np.sum(np.multiply(ptm1, qt), axis=1)
			pt_qtm1 = np.sum(np.multiply(pt, qtm1), axis=1)
			ptm1_qtm1 = np.sum(np.multiply(ptm1, qtm1), axis=1)

			if self.mtype == 'price':
				paasche = np.true_divide(pt_qt, ptm1_qt)
				laspeyres = np.true_divide(pt_qtm1, ptm1_qtm1)

			elif self.mtype == 'quantity':
				paasche = np.true_divide(pt_qt, pt_qtm1)
				laspeyres = np.true_divide(ptm1_qt, ptm1_qtm1)

			links = np.sqrt(np.multiply(paasche, laspeyres))
			chain = np.cumprod(np.insert(links, 0, 1))

			fisher = pd.Series(
				chain,
				index=self.price.index,
				name=f'fisher_{self.mtype}'
			)

			scale = rbase.compute_base_value(fisher)
			return 100 * (fisher / scale)


		else:
			# locate price and quantity values in base period, average them in case
			#	the base period is an entire year
			idx = rbase.locate_base_periods(self.price)
			pb = np.mean(parr[idx, :], axis=0)
			qb = np.mean(qarr[idx, :], axis=0)

			pt_qt = np.sum(np.multiply(parr, qarr), axis=1)
			pb_qt = np.sum(np.multiply(pb, qarr), axis=1)
			pt_qb = np.sum(np.multiply(parr, qb), axis=1)
			pb_qb = np.dot(pb, qb)

			if self.mtype == 'price':
				paasche = np.true_divide(pt_qt, pb_qt)
				laspeyres = np.true_divide(pt_qb, pb_qb)

			elif self.mtype == 'quantity':
				paasche = np.true_divide(pt_qt, pt_qb)
				laspeyres = np.true_divide(pb_qt, pb_qb)

			return pd.Series(
				100 * np.sqrt(np.multiply(paasche, laspeyres)),
				index=self.price.index,
				name=f'fisher_{self.mtype}'
			)



class _TornqvistIndexConstructor(_IndexConstructor):

	def compute(self, base):

		rbase = _IndexRebaser(True, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		pt = parr[1:, :]
		qt = qarr[1:, :]
		prod_t = np.multiply(pt, qt)
		weight_t = np.true_divide(prod_t, np.sum(prod_t, axis=1, keepdims=True))

		ptm1 = parr[:-1, :]
		qtm1 = qarr[:-1, :]
		prod_tm1 = np.multiply(ptm1, qtm1)
		weight_tm1 = np.true_divide(prod_tm1, np.sum(prod_tm1, axis=1, keepdims=True))

		share_t = 1/2
		weights = share_t * weight_t + (1-share_t) * weight_tm1

		if self.mtype == 'price':
			paths = np.log(np.true_divide(pt, ptm1))

		elif self.mtype == 'quantity':
			paths = np.log(np.true_divide(qt, qtm1))

		log_links = np.sum(np.multiply(paths, weights), axis=1)
		links = np.exp(log_links)
		chain = np.cumprod(np.insert(links, 0, 1))

		tornqvist = pd.Series(
			chain,
			index=self.price.index,
			name=f'tornqvist_{self.mtype}'
		)

		scale = rbase.compute_base_value(tornqvist)
		return 100 * (tornqvist / scale)



class _WalshIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:
			pt, qt = parr[1:, :], qarr[1:, :]
			ptm1, qtm1 = parr[:-1, :], qarr[:-1, :]

			if self.mtype == 'price':
				weights = np.sqrt(np.multiply(qt, qtm1))
				paths, scales = pt, ptm1

			elif self.mtype == 'quantity':
				weights = np.sqrt(np.multiply(pt, ptm1))
				paths, scales = qt, qtm1

			numer = np.sum(np.multiply(paths, weights), axis=1)
			denom = np.sum(np.multiply(scales, weights), axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			walsh = pd.Series(
				chain,
				index=self.price.index,
				name=f'walsh_{self.mtype}'
			)

			scale = rbase.compute_base_value(walsh)
			return 100 * (walsh / scale)

		else:
			# locate price and quantity values in base period, average them in case
			#	the base period is an entire year
			idx = rbase.locate_base_periods(self.price)
			pb = np.mean(parr[idx, :], axis=0)
			qb = np.mean(qarr[idx, :], axis=0)

			if self.mtype == 'price':
				weights = np.sqrt(np.multiply(qarr, qb))
				paths, scales = parr, pb

			elif self.mtype == 'quantity':
				weights = np.sqrt(np.multiply(parr, pb))
				paths, scales = qarr, qb

			numer = np.sum(np.multiply(paths, weights), axis=1)
			denom = np.sum(np.multiply(scales, weights), axis=1)

			return pd.Series(
				100 * np.true_divide(numer, denom),
				index=self.price.index,
				name=f'walsh_{self.mtype}'
			)



class _GeometricIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:
			pt, qt = parr[1:, :], qarr[1:, :]
			ptm1, qtm1 = parr[:-1, :], qarr[:-1, :]

			# weights are same for price or quantity mtypes
			ptm1_qtm1 = np.multiply(ptm1, qtm1)
			weights = np.true_divide(ptm1_qtm1, np.sum(ptm1_qtm1, axis=1, keepdims=True))

			if self.mtype == 'price':
				paths = np.true_divide(pt, ptm1)

			elif self.mtype == 'quantity':
				paths = np.true_divide(qt, qtm1)

			links = np.prod(np.power(paths, weights), axis=1)
			chain = np.cumprod(np.insert(links, 0, 1))

			geometric = pd.Series(
				chain,
				index=self.price.index,
				name=f'geometric_{self.mtype}'
			)

			scale = rbase.compute_base_value(geometric)
			return 100 * (geometric / scale)

		else:
			# locate price and quantity values in base period, average them in case
			#	the base period is an entire year
			idx = rbase.locate_base_periods(self.price)
			pb = np.mean(parr[idx, :], axis=0)
			qb = np.mean(qarr[idx, :], axis=0)

			# weights are same for price or quantity mtypes
			weights = np.multiply(pb, qb) / np.dot(pb, qb)

			if self.mtype == 'price':
				paths = np.true_divide(parr, pb)

			elif self.mtype == 'quantity':
				paths = np.true_divide(qarr, qb)

			return pd.Series(
				100 * np.prod(np.power(paths, weights), axis=1),
				index=self.price.index,
				name=f'geometric_{self.mtype}'
			)



class _MarshallEdgeworthIndexConstructor(_IndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		parr, qarr = self.price.to_numpy(), self.quantity.to_numpy()

		if chained:
			pt, qt = parr[1:, :], qarr[1:, :]
			ptm1, qtm1 = parr[:-1, :], qarr[:-1, :]

			if self.mtype == 'price':
				weights = qt + qtm1
				numer = np.sum(np.multiply(pt, weights), axis=1)
				denom = np.sum(np.multiply(ptm1, weights), axis=1)

			elif self.mtype == 'quantity':
				weights = pt + ptm1
				numer = np.sum(np.multiply(qt, weights), axis=1)
				denom = np.sum(np.multiply(qtm1, weights), axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			marshall = pd.Series(
				chain,
				index=self.price.index,
				name=f'marshedge_{self.mtype}'
			)

			scale = rbase.compute_base_value(marshall)
			return 100 * (marshall / scale)

		else:
			# locate price and quantity values in base period, average them in case
			#	the base period is an entire year
			idx = rbase.locate_base_periods(self.price)
			pb = np.mean(parr[idx, :], axis=0)
			qb = np.mean(qarr[idx, :], axis=0)

			if self.mtype == 'price':
				weights = qarr + qb
				numer = np.sum(np.multiply(parr, weights), axis=1)
				denom = np.sum(np.multiply(pb, weights), axis=1)

			elif self.mtype == 'quantity':
				weights = parr + pb
				numer = np.sum(np.multiply(qarr, weights), axis=1)
				denom = np.sum(np.multiply(qb, weights), axis=1)

			return pd.Series(
				100 * np.true_divide(numer, denom),
				index=self.price.index,
				name=f'marshedge_{self.mtype}'
			)



class _UnweightedIndexConstructor(object):

	def __init__(
		self,
		data: Union[Series, DataFrame]
	):

		if not isinstance(data, (pd.Series, pd.DataFrame)):
			raise TypeError(
				f"{type(quantity)}. 'data' must be pandas Series or DataFrame"
			)

		# ensure data are DataFrames, just so subclasses don't have to have
		#	a series of checks
		try:
			self.data = data.to_frame()
		except AttributeError:
			self.data = data



class _CarliIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			links = np.mean(np.true_divide(arr[1:, :], arr[:-1, :]), axis=1)
			chain = np.cumprod(np.insert(links, 0, 1))

			carli = pd.Series(
				chain,
				index=self.data.index,
				name='carli_index'
			)

			scale = rbase.compute_base_value(carli)
			return 100 * (carli / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.mean(arr[idx, :], axis=0)

			return pd.Series(
				100 * np.mean(np.true_divide(arr, base), axis=1),
				index=self.data.index,
				name='carli_index'
			)



class _DutotIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			numer = np.sum(arr[1:, :], axis=1)
			denom = np.sum(arr[:-1, :], axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			dutot = pd.Series(
				chain,
				index=self.data.index,
				name='dutot_index'
			)

			scale = rbase.compute_base_value(dutot)
			return 100 * (dutot / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.sum(np.mean(arr[idx, :], axis=0))

			return pd.Series(
				100 * np.true_divide(np.sum(arr, axis=1), base),
				index=self.data.index,
				name='dutot_index'
			)



class _JevonsIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			prod = np.prod(np.true_divide(arr[1:, :], arr[:-1, :]), axis=1)

			links = np.power(prod, arr.shape[1])
			chain = np.cumprod(np.insert(links, 0, 1))

			jevons = pd.Series(
				chain,
				index=self.data.index,
				name='jevons_index'
			)

			scale = rbase.compute_base_value(jevons)
			return 100 * (jevons / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.mean(arr[idx, :], axis=0)

			prod = np.prod(np.true_divide(arr, base), axis=1)
			return pd.Series(
				100 * np.power(prod, arr.shape[1]),
				index=self.data.index,
				name='jevons_index'
			)



class _HarmonicMeanIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			avg = np.mean(np.true_divide(arr[:-1, :], arr[1:, :]), axis=1)

			links = np.true_divide(1, avg)
			chain = np.cumprod(np.insert(links, 0, 1))

			harmmean = pd.Series(
				chain,
				index=self.data.index,
				name='harmmean_index'
			)

			scale = rbase.compute_base_value(harmmean)
			return 100 * (harmmean / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.mean(arr[idx, :], axis=0)

			avg = np.mean(np.true_divide(base, arr), axis=1)
			return pd.Series(
				100 * np.true_divide(1, avg),
				index=self.data.index,
				name='harmmean_index'
			)



class _CSWDIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			carli_terms = np.true_divide(arr[1:, :], arr[:-1, :])
			carli_links = np.sum(carli_terms, axis=1)

			harmmean_links = np.sum(np.reciprocal(carli_terms), axis=1)

			links = np.true_divide(carli_links, harmmean_links)
			chain = np.cumprod(np.sqrt(np.insert(links, 0, 1)))

			cswd = pd.Series(
				chain,
				index=self.data.index,
				name='cswd_index'
			)

			scale = rbase.compute_base_value(cswd)
			return 100 * (cswd / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.mean(arr[idx, :], axis=0)

			carli_terms = np.true_divide(arr, base)
			harmmean_terms = np.reciprocal(carli_terms)

			carli = np.sum(carli_terms, axis=1)
			harmmean = np.sum(harmmean_terms, axis=1)

			return pd.Series(
				100 * np.true_divide(carli, harmmean),
				index=self.data.index,
				name='cswd_index'
			)



class _HarmonicRatioIndexConstructor(_UnweightedIndexConstructor):

	def compute(self, chained, base):

		rbase = _IndexRebaser(chained, base)
		arr = self.data.to_numpy()

		if chained:
			numer = np.sum(np.reciprocal(arr[:-1, :]), axis=1)
			denom = np.sum(np.reciprocal(arr[1:, :]), axis=1)

			links = np.true_divide(numer, denom)
			chain = np.cumprod(np.insert(links, 0, 1))

			harmrat = pd.Series(
				chain,
				index=self.data.index,
				name='harmrat_index'
			)

			scale = rbase.compute_base_value(harmrat)
			return 100 * (harmrat / scale)

		else:
			# locate values in base period, average them in case the base period
			#	is an entire year
			idx = rbase.locate_base_periods(self.data)
			base = np.mean(arr[idx, :], axis=0)

			numer = np.sum(np.reciprocal(base))
			denom = np.sum(np.reciprocal(arr), axis=1)

			return pd.Series(
				100 * np.true_divide(numer, denom),
				index=self.data.index,
				name='harmrat_index'
			)



class _IndexRebaser(object):

	def __init__(self, chained, base):
		if not isinstance(chained, bool):
			raise TypeError(f"{type(chained)}. 'chained' must be a bool")

		if isinstance(base, int):
			# an entire year is used as the base period
			pass
		else:
			# let pandas handle any type errors and interpretion
			base = pd.Timestamp(base)

		self.chained = chained
		self.base = base

	def locate_base_periods(self, data):
		"""
		create a boolean numpy array of indicators for observations in the base
		period
		"""
		if not isinstance(data.index, pd.DatetimeIndex):
			raise TypeError(f"{type(data)}. indexing data must have DatetimeIndex")

		if isinstance(self.base, int):
			idx = (data.index.year >= self.base) & (data.index.year <= self.base)
			if not idx.any():
				raise ValueError(
					f"cannot locate base period. no data in year {self.base}"
				)
		else:
			idx = data.index == self.base
			if not idx.any():
				raise ValueError(f"cannot locate base period. no data in {self.base}")

		return idx

	def compute_base_value(self, data):
		if not isinstance(data.index, pd.DatetimeIndex):
			raise TypeError(f"{type(data)}. indexing data must have DatetimeIndex")

		idx = self.locate_base_periods(data)
		return np.mean(data.loc[idx])
