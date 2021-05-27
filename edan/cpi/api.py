"""
module that prepares the CPI component table
"""

from edan.algos import construct_forest
from edan.aggregates.tables import Table
from edan.aggregates.register import registry

from edan.cpi.core import CPIComponent


flat_cpi = [CPIComponent.from_registry(e) for e in registry.by_table('cpi')]
construct_forest(flat_cpi, level='level', lower='subs')

CPITable = Table(flat_cpi, 'CPI')
