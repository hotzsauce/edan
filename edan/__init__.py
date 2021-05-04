"""
first pass at an economic data analysis toolkit, with some vague intent to learn
more about the NIPA/PCE accounts, and financial markets - specifically treasuries
and other interest rate-related markets

'edan' <- e(conomic) d(ata) an(alysis)
"""

import edan.nipa
import edan.fetch

__all__ = ['nipa', 'fetch']
