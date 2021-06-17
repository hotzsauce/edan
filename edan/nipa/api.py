"""
module that prepares the GDP & PCE component table
"""

from edan.algos import construct_forest
from edan.core.tables import Table
from edan.core.register import registry

from edan.nipa.core import component_type


flat_pce = []
for entry in registry.by_table('pce'):
	comp = component_type(entry['__ctype__'])
	flat_pce.append(comp.from_registry(entry))

flat_gdp = []
for entry in registry.by_table('gdp'):
	comp = component_type(entry['__ctype__'])
	flat_gdp.append(comp.from_registry(entry))

construct_forest(flat_pce, level='level', lower='subs')
construct_forest(flat_gdp, level='level', lower='subs')

PCETable = Table(flat_pce, 'PCE')
GDPTable = Table(flat_gdp, 'GDP')
