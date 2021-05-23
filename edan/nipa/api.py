"""
module that prepares the GDP component tree
"""

from __future__ import annotations


from edan.algos import construct_forest
from edan.aggregates.tables import Table
# from edan.nipa.tables import NIPATable

from edan.nipa.register import registry
from edan.nipa.components import NIPAComponent


# from the linear collection of Components - organized first by BEA table, then
#	by row within that table - construct a list of the top-level components within
#	those tables, with the `subs` attribute filled in with the appropriate
#	Component objects
components = [NIPAComponent.from_registry(v) for v in registry.registry.values()]
organized_comps = construct_forest(components, level='level', lower='subs')

# need a better way to partition the recorded components
pce_components = [c for c in components if 'pce' in c.code[:4]]
gdp_components = [c for c in components if 'gdp' in c.code[:4]]

PCETable = Table(pce_components, 'PCE')
GDPTable = Table(gdp_components, 'GDP')
