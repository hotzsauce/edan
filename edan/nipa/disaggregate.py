"""
selecting subcomponents & disaggregated series of Component objects
"""

from __future__ import annotations

from edan.delims import (
	concat_codes,
	contains
)



def recursive_subcomponent(comp: Component, target: str):
	"""
	recursively search for subcomponent with code `target`
	"""

	if comp.code == target:
		return comp

	for sub in comp.subs:
		if contains(sub.code, target):
			return recursive_subcomponent(sub, target)


class Disaggregator(object):

	def __init__(
		self,
		component: Component,
		subcomponents: Iterable[str] = [],
		level: int = 0
	):

		"""
		class for selecting subcomponents of a component that are further down the
		subcomponent tree than just the Component objects immediately available in
		the `subs` attribute. functionality for selecting based on `edan` code and
		level relative to the Component is provided

		Parameters
		----------
		subs : str | list ( = [] )
			an iterable of subcomponents to return. the elements of `subs` are
			assumed to be (relative or absolute) `edan` codes
		level : int ( = 0 )
			the level, relative to the current Component, of subcomponents that
			are to be returned. if a subcomponent has level `l`, with
			l < level + component.level, and that subcomponent is elemental, it is
			included
		"""
		self.disaggregates = []
		self.component = component

		if subcomponents:

			for code in subcomponents:
				# concatenate later ids if `code` isn't an absolute edan code
				abs_code = concat_codes(component.code, code)

				for sub in component.subs:

					if sub.code == abs_code:
						# `subcomponents` references an immediate subcomponent
						self.disaggregates.append(sub)

					elif contains(sub.code, abs_code):
						# `subcomponents` references a subcomponent further down
						comp = recursive_subcomponent(sub, abs_code)
						self.disaggregates.append(comp)

		elif level:
			abs_level = level + component.level
			self.recursive_level(component, abs_level)

	def recursive_level(self, comp: Component, level: int):
		if comp.level < level:
			if comp.elemental:
				self.disaggregates.append(comp)
			else:
				for sub in comp.subs:
					self.recursive_level(sub, level)

		elif comp.level == level:
			self.disaggregates.append(comp)

	def __iter__(self):
		for sub in self.disaggregates:
			yield sub

	def __str__(self):
		return f"Disaggregator({repr(self.component)})"
