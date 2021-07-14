"""
module that prepares the CES employment table
"""

from edan.algos import construct_forest
from edan.core.tables import Table
from edan.core.register import registry

from edan.ces.core import CESComponent

flat_ces = []
for entry in registry.by_table('ces'):
	flat_ces.append(CESComponent.from_registry(entry))

construct_forest(flat_ces, level='level', lower='subs')

CESTable = Table(flat_ces, 'CES')
