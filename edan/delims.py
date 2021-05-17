"""
tools for working with the `edan` delimiters & hierarchical codes
"""

from __future__ import annotations

import re
from itertools import cycle

from rich import print

edan_delimiters = (':', '-', '+')
delim_pattern = '|'.join(map(re.escape, edan_delimiters))


class EdanCode(object):

	def __init__(self, code: str):
		self.code = code
		self.ids = re.split(delim_pattern, code)
		self.delims = re.findall(delim_pattern, code)

	def __repr__(self):
		return f"EdanCode({self.code})"

	def __str__(self):
		return self.code

	def __getitem__(self, key):
		if isinstance(key, int):
			return self.ids[key]
		elif isinstance(key, slice):
			ids = self.ids[key]

			if len(ids) == 1:
				return ids[0]
			delims = [self.delims[i] for i, id_ in enumerate(self.ids) if id_ in ids[:-1]]

			spliced_code = [i for pair in zip(ids, delims+['']) for i in pair]
			return ''.join(spliced_code)

		raise TypeError(repr(key))



def concat_codes(code: str, other: str, delim: str = ':'):
	"""
	concatenate two possibly overlapping `edan` code-like strings to produce a
	third code-like string. if the last portion of `code` is identical to the
	first portion of `other`, then only the non-overlapping portion of `other`
	is concatenated to the entirety of `code`. if there is no shared section,
	then `code` and `other` are conctatenated as-is, with the provided delimiter

	Parameters
	----------
	code : str
		the beginning string to concatenate
	other : str
		the ending string to concatenate
	delim : str
		the delimiter used to join `code` and `other` if there is no overlap
	"""
	code, other = EdanCode(code), EdanCode(other)
	n_overlaps = max(len(code.ids), len(other.ids))

	for i in range(1, n_overlaps+1):
		if code[-i:] == other[:i]:

			base = code[:i]
			addition = other[(i-1):]

			return base + code.delims[-1] + addition

	if delim not in edan_delimiters:
		raise ValueError(f"{repr(delim)} is not a recognized edan delimiter")
	return str(code) + delim + str(other)
