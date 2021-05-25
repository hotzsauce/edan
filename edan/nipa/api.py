"""
module that prepares the GDP & PCE component table
"""

import pathlib

from edan.algos import construct_forest
from edan.aggregates.tables import Table
from edan.aggregates.register import ComponentRegistry

from edan.nipa.core import NIPAComponent

# create registry based on JSON in edan/nipa
registry_filename = '.registry.json'
nipa_registry = pathlib.Path(__file__).parent / registry_filename
registry = ComponentRegistry(nipa_registry, 'NIPA')

# from the linear collection of Components - organized first by BEA table, then
#	by row within that table - construct a list of the top-level components within
#	those tables, with the `subs` attribute filled in with the appropriate
#	Component objects
components = [NIPAComponent.from_registry(v) for v in registry.registry.values()]
organized_comps = construct_forest(components, level='level', lower='subs')

pce_components = [c for c in components if c.subject == 'pce']
gdp_components = [c for c in components if c.subject == 'gdp']

PCETable = Table(pce_components, 'PCE')
GDPTable = Table(gdp_components, 'GDP')
