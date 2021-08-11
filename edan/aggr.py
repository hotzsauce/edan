"""
aggregating components into custom aggregates
"""

from __future__ import annotations

from edan.utils.dtypes import iterable_not_string

from edan.core.base import BaseComponent
from edan.nipa.aggr import aggregate_nipa


def aggregate(
	objs: Iterable[Component],
	code: str = '',
	level: int = 0,
	long_name = '',
	short_name = '',
):
	"""
	aggregate a collection of components into a so-called 'synthetic' component.
	the method of aggregation for each mtype of the basket of components will
	vary by each recognized `edan` concept; i.e. NIPA, CPI, etc. see the `aggr`
	module in each `edan` submodule for details.
		for all `edan` concepts, every component in `objs` must come from the
	same source ('BEA', 'BLS', etc.), and, must satisfy the stricter requirement
	that they belong in the same table (in BEA, 'GDP' or 'PCE' tables)  of that
	source. a ValueError is thrown if all components don't belong to the same
	source or table. this is not necessary per se, but it makes the code on the
	back end more simple, and aggregating things like PCE inflation and CPI
	inflation measures, or GDP and employment numbers, don't really make sense.

	Note
	----
	for the moment only NIPA components can be aggregated

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

	Returns
	-------
	Component
	"""
	if iterable_not_string(objs):
		# ensure all components come from the same table
		tables, sources = [], []
		for obj in objs:
			if not isinstance(obj, BaseComponent):
				raise TypeError("every elements of must be a Component")
			tables.append(obj.table)
			sources.append(obj.source)

		def all_equal(iterator):
			iterator = iter(iterator)
			try:
				first = next(iterator)
			except StopIteration:
				return True
			return all(first == x for x in iterator)

		if not all_equal(tables):
			raise ValueError("can only aggregate Components from the same table")

		if not all_equal(sources):
			raise ValueError("can only aggregate Components from the same source")

		try:
			table = tables[0]
			aggr_func = table_aggregators[table]

			return aggr_func(
				objs=objs,
				code=code,
				level=level,
				long_name=long_name,
				short_name=short_name,
				table=table
			)

		except KeyError:
			raise NotImplementedError(
				f"no aggregator function available for the {table} table"
			)

	else:
		raise TypeError("`objs` must be an iterable of Components")


table_aggregators = {
	'pce': aggregate_nipa,
	'gdp': aggregate_nipa
}
