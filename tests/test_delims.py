"""
testing edan/delims module
"""

import unittest

from edan.delims import (
	EdanCode,
	contains,
	concat_codes
)

test_code = EdanCode('a:b-c:d+e')

class TestEdanCode(unittest.TestCase):

	def test_integer_indexing(self):
		with self.subTest(): self.assertEqual(test_code[0], 'a')
		with self.subTest(): self.assertEqual(test_code[1], 'b')
		with self.subTest(): self.assertEqual(test_code[2], 'c')
		with self.subTest(): self.assertEqual(test_code[3], 'd')
		with self.subTest(): self.assertEqual(test_code[4], 'e')

	def test_integer_neg_indexing(self):
		with self.subTest(): self.assertEqual(test_code[-1], 'e')
		with self.subTest(): self.assertEqual(test_code[-2], 'd')
		with self.subTest(): self.assertEqual(test_code[-3], 'c')
		with self.subTest(): self.assertEqual(test_code[-4], 'b')
		with self.subTest(): self.assertEqual(test_code[-5], 'a')

	def test_slice_indexing_boundaries(self):
		with self.subTest(): self.assertEqual(test_code[:1], 'a')
		with self.subTest(): self.assertEqual(test_code[-1:], 'e')
		with self.subTest(): self.assertEqual(test_code[:0], '')
		with self.subTest(): self.assertEqual(test_code[0:], 'a:b-c:d+e')

	def test_slice_indexing_no_start(self):
		with self.subTest(): self.assertEqual(test_code[:2], 'a:b')
		with self.subTest(): self.assertEqual(test_code[:-3], 'a:b')

	def test_slice_indexing_no_stop(self):
		with self.subTest(): self.assertEqual(test_code[2:], 'c:d+e')
		with self.subTest(): self.assertEqual(test_code[-3:], 'c:d+e')

	def test_slice_indexing_start_stop(self):
		with self.subTest(): self.assertEqual(test_code[1:4], 'b-c:d')
		with self.subTest(): self.assertEqual(test_code[-4:-1], 'b-c:d')
		with self.subTest(): self.assertEqual(test_code[0:3], 'a:b-c')


class TestDelimMethods(unittest.TestCase):

	def test_contains_simple(self):
		parent = 'a:b:c'
		child = 'a:b:c:d:e'
		self.assertTrue(contains(parent, child))

	def test_contains_exact(self):
		parent = 'a:b:c'
		child = 'a:b:c'
		self.assertTrue(contains(parent, child))

	def test_contains_same_length(self):
		parent = 'a:b:c'
		child = 'd:e:f'
		self.assertFalse(contains(parent, child))

	def test_contains_diff_delim(self):
		parent = 'a:b:c'
		child = 'a-b:c:d'
		self.assertFalse(contains(parent, child))

	def test_contains_long_parent(self):
		parent = 'a:b-c:d+e'
		child = 'a:b'
		self.assertFalse(contains(parent, child))

	def test_concat_simple(self):
		parent = 'a:b'
		child = 'c-d'
		self.assertEqual(concat_codes(parent, child), 'a:b:c-d')

	def test_concat_single_overlap(self):
		parent = 'a:b'
		child = 'b-c'
		self.assertEqual(concat_codes(parent, child), 'a:b-c')

	def test_concat_multi_overlap(self):
		parent = 'a:b:c'
		child = 'b:c-d'
		self.assertEqual(concat_codes(parent, child), 'a:b:c-d')

	def test_concat_complete_overlap(self):
		parent = 'a:b'
		child = 'a:b:c-d'
		self.assertEqual(concat_codes(parent, child), 'a:b:c-d')

	def test_concat_bad_delimiter(self):
		parent = 'a:b'
		child = 'c-d'
		with self.assertRaises(ValueError):
			_ = concat_codes(parent, child, '|')


if __name__ == '__main__':
	unittest.main()
