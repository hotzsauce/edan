"""
tools for working with the `edan` delimiters & hierarchical codes
"""

from __future__ import annotations

import re
from itertools import cycle

from rich import print

edan_delimiters = (':', '~')
delim_pattern = '|'.join(map(re.escape, edan_delimiters))


class EdanCode(object):

	def __init__(self, code: str):
		if isinstance(code, EdanCode):
			self.code = str(code)
		else:
			self.code = code

		ids = re.split(delim_pattern, code)
		delims = re.findall(delim_pattern, code)

		self.elements = [None]*(len(ids) + len(delims))
		self.elements[::2] = ids
		self.elements[1::2] = delims

	@property
	def ids(self):
		return self.elements[::2]

	@property
	def delims(self):
		return self.elements[1::2]

	def __repr__(self):
		return f"EdanCode({self.code})"

	def __str__(self):
		return self.code

	def __len__(self):
		return (len(self.elements) + 1) // 2

	def __getitem__(self, key):
		if isinstance(key, int):
			if key >= 0:
				return self.elements[2*key]
			else:
				return self.elements[2*key+1]

		elif isinstance(key, slice):
			if (key.stop is None) and (key.start is None):
				elms = self.elements[slice(None, None, key.step)]

			elif key.stop is None:
				b = 1 if key.start < 0 else 0
				elms = self.elements[slice(2*key.start+b, None, key.step)]

			elif key.start is None:
				e = 0 if key.stop <= 0 else -1
				elms = self.elements[slice(None, 2*key.stop+e, key.step)]

			else:
				b = 1 if key.start < 0 else 0
				e = 0 if key.stop <= 0 else -1
				elms = self.elements[slice(2*key.start+b, 2*key.stop+e, key.step)]

			return ''.join(elms)

		raise TypeError(f"{repr(key)}. EdanCode key can only be `int` or `slice`")


def contains(parent: str, child: str):
	"""
	boolean function returning True if EdanCode `child` is descended from
	EdanCode `parent`
	"""

	parent, child = EdanCode(parent), EdanCode(child)

	base_level, child_level = len(parent), len(child)
	if base_level > child_level:
		return False
	elif base_level == child_level:
		if str(parent) == str(child):
			return True

	child_base = child[:base_level]
	return str(parent) == child_base


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

	if contains(code, other):
		return other

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
