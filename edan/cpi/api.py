"""
module that prepares the CPI component table
"""

from edan.algos import construct_forest
from edan.aggregates.tables import Table

from edan.cpi.register import registry
from edan.cpi.core import CPIComponent

# from the linear collection of Components - organized first by BEA table, then
#	by row within that table - construct a list of the top-level components wihin
#	those tables, with the `subs` attribute filled in with the appropriate
#	Component objects
components = [CPIComponent.from_registry(v) for v in registry.registry.values()]
organized_comps = construct_forest(components, level='level', lower='subs')

CPITable = Table(components, 'CPI')
