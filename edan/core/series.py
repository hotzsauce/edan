"""
base container objects for singular data series
"""

from __future__ import annotations

import pandas as pd

from edan.core.base import BaseSeries
from edan.data.retrieve import retriever


class Series(BaseSeries):

	def __init__(
		self,
		code: str = '',
		mtype: str = '',
		source: str = '',
		comp: Component = None
	):
		if code:
			data, meta = retriever.retrieve(code, source=source)
		else:
			data, meta = pd.Series(), pd.Series()

		self.code = code
		self.data = data
		self.meta = meta


		self.mtype = mtype
		self.comp = comp
		if self.comp:
			self.long_name = self.comp.long_name
			self.short_name = self.comp.short_name
		else:
			self.long_name, self.short_name = '', ''

	def __repr__(self):
		klass = self.__class__.__name__
		return f"{klass}({self.code})"
