"""
testing the ModificationAccessor's calculations and that it correctly interprets
the variety of different ways it can be called
"""

import unittest

from edan.aggregates.modifications import ModificationAccessor

import pandas as pd
import numpy as np
from numpy.testing import (
	assert_array_equal as aequal, # returns None if equal
	assert_array_almost_equal as approx_equal
)

from rich import print



class DataWrapper(object):
	"""
	ModificationAccessor has `self.data = obj.data` in init; just need
	to wrap a pandas DataFrame
	"""
	def __init__(self, data):
		self.data = data


N = 10
test_data = pd.Series(
	data=np.random.random_sample(N),
	index=pd.date_range(end='1/1/2021', periods=N, freq='q'),
	name='test'
)
wrapper = DataWrapper(test_data)
test_mod = ModificationAccessor(wrapper)


test_arr = test_data.values

class TestModificationAccessor(unittest.TestCase):

	def new_blank(self):
		arr = np.empty(N)
		arr[:] = np.nan
		return arr

	def test_diff(self):
		diff = self.new_blank()
		diff[1:] = test_arr[1:] - test_arr[:-1]
		self.assertIsNone(aequal(diff, test_mod('diff').values))

	def test_diff_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = test_arr[n:] - test_arr[:-n]
		self.assertIsNone(aequal(diff, test_mod('diff', n=n).values))

	def test_diffp(self):
		diff = self.new_blank()
		diff[1:] = 100 * (test_arr[1:]/test_arr[:-1] - 1)
		self.assertIsNone(aequal(diff, test_mod('diff%').values))

	def test_diffp_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = 100 * (test_arr[n:]/test_arr[:-n] - 1)
		self.assertIsNone(aequal(diff, test_mod('diff%', n=n).values))

	def test_diffl(self):
		diff = self.new_blank()
		diff[1:] = 100 * np.log(test_arr[1:]/test_arr[:-1])
		self.assertIsNone(aequal(diff, test_mod('diffl').values))

	def test_diffl_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = 100 * np.log(test_arr[n:]/test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('diffl', n=n).values))

	def test_difa(self):
		diff = self.new_blank()
		diff[1:] = 4 * (test_arr[1:] - test_arr[:-1])
		self.assertIsNone(aequal(diff, test_mod('difa').values))

	def test_difa_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = (4/n) * (test_arr[n:] - test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('difa', n=n).values))

	def test_difa_nh(self):
		n, h = 3, 2
		diff = self.new_blank()
		diff[n:] = (h/n) * (test_arr[n:] - test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('difa', n=n, h=h).values))

	def test_difap(self):
		diff = self.new_blank()
		diff[1:] = 100 * ( (test_arr[1:] / test_arr[:-1])**4 - 1 )
		self.assertIsNone(aequal(diff, test_mod('difa%').values))

	def test_difap_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = 100 * ( (test_arr[n:] / test_arr[:-n])**(4/n) - 1 )
		self.assertIsNone(aequal(diff, test_mod('difa%', n=n).values))

	def test_difap_nh(self):
		n, h = 3, 2
		diff = self.new_blank()
		diff[n:] = 100 * ( (test_arr[n:] / test_arr[:-n])**(h/n) - 1 )
		self.assertIsNone(aequal(diff, test_mod('difa%', n=n, h=h).values))

	def test_difal(self):
		diff = self.new_blank()
		diff[1:] = 100 * 4 * np.log(test_arr[1:] / test_arr[:-1])
		self.assertIsNone(aequal(diff, test_mod('difal').values))

	def test_difal_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = 100 * (4/n) * np.log(test_arr[n:] / test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('difal', n=n).values))

	def test_difal_nh(self):
		n, h = 3, 2
		diff = self.new_blank()
		diff[n:] = 100 * (h/n) * np.log(test_arr[n:] / test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('difal', n=n, h=h).values))

	def test_difv(self):
		diff = self.new_blank()
		diff[1:] = test_arr[1:] - test_arr[:-1]
		self.assertIsNone(aequal(diff, test_mod('difv').values))

	def test_difv_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = (test_arr[n:] - test_arr[:-n]) / n
		self.assertIsNone(aequal(diff, test_mod('difv', n=n).values))

	def test_difvp(self):
		diff = self.new_blank()
		diff[1:] = 100 * ( (test_arr[1:] / test_arr[:-1]) ** 4 - 1)
		self.assertIsNone(aequal(diff, test_mod('difv%').values))

	def test_difvp_nh(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = 100 * ( (test_arr[n:] / test_arr[:-n]) ** (4/n) - 1)
		self.assertIsNone(aequal(diff, test_mod('difv%', n=n, h=h).values))

	def test_difvp_nh(self):
		n, h = 3, 2
		diff = self.new_blank()
		diff[n:] = 100 * ( (test_arr[n:] / test_arr[:-n]) ** (h/n) - 1)
		self.assertIsNone(aequal(diff, test_mod('difv%', n=n, h=h).values))

	def test_difvl(self):
		diff = self.new_blank()
		diff[1:] = 100 * np.log(test_arr[1:] / test_arr[:-1])
		self.assertIsNone(aequal(diff, test_mod('difvl').values))

	def test_difvl_n(self):
		n = 3
		diff = self.new_blank()
		diff[n:] = (100/n) * np.log(test_arr[n:] / test_arr[:-n])
		self.assertIsNone(aequal(diff, test_mod('difvl', n=n).values))

	def test_movv_n(self):
		# using `aequal` throws errors b/c of differences on the order of 1.5e-16
		n = 3
		movv = self.new_blank()
		for i in range(n-1, len(movv)):
			movv[i] = np.mean(test_arr[i-n+1:i+1])
		self.assertIsNone(approx_equal(movv, test_mod('movv', n=n).values))

	def test_mova_nh(self):
		# using `aequal` throws errors b/c of differences on the order of 1.5e-16
		n, h = 3, 2
		movv = self.new_blank()
		for i in range(n-1, len(movv)):
			movv[i] = h * np.mean(test_arr[i-n+1:i+1])
		self.assertIsNone(approx_equal(movv, test_mod('mova', n=n, h=h).values))

	def test_movt_n(self):
		# using `aequal` throws errors b/c of differences on the order of 1.7e-16
		n = 3
		movv = self.new_blank()
		for i in range(n-1, len(movv)):
			movv[i] = np.sum(test_arr[i-n+1:i+1])
		self.assertIsNone(approx_equal(movv, test_mod('movt', n=n).values))

	def test_yryr(self):
		yryr = self.new_blank()
		yryr[4:] = test_arr[4:] - test_arr[:-4]
		self.assertIsNone(aequal(yryr, test_mod('yryr').values))

	def test_yryr_h(self):
		h = 3
		yryr = self.new_blank()
		yryr[h:] = test_arr[h:] - test_arr[:-h]
		self.assertIsNone(aequal(yryr, test_mod('yryr', h=h).values))

	def test_yryrp(self):
		yryr = self.new_blank()
		yryr[4:] = 100 * (test_arr[4:] / test_arr[:-4] - 1)
		self.assertIsNone(aequal(yryr, test_mod('yryr%').values))

	def test_yryrp_h(self):
		h = 3
		yryr = self.new_blank()
		yryr[h:] = 100 * (test_arr[h:] / test_arr[:-h] - 1)
		self.assertIsNone(aequal(yryr, test_mod('yryr%', h=h).values))

	def test_yryrl(self):
		yryr = self.new_blank()
		yryr[4:] = 100 * np.log(test_arr[4:] / test_arr[:-4])
		self.assertIsNone(aequal(yryr, test_mod('yryrl').values))

	def test_yryrl_h(self):
		h = 3
		yryr = self.new_blank()
		yryr[h:] = 100 * np.log(test_arr[h:] / test_arr[:-h])
		self.assertIsNone(aequal(yryr, test_mod('yryrl', h=h).values))

	def test_call(self):
		f = lambda s: s - 1

		arr = self.new_blank()
		arr = test_arr - 1
		self.assertIsNone(aequal(arr, test_mod(f).values))

	def test_call_positional(self):
		f = lambda s, a: s + a

		arg_vec = np.random.random_sample(N)
		arr = self.new_blank()
		arr = test_arr + arg_vec

		self.assertIsNone(aequal(arr, test_mod(f, arg_vec).values))

	def test_call_keyword(self):
		f = lambda s, a: s - a

		arg_vec = np.random.random_sample(N)
		arr = self.new_blank()
		arr = test_arr - arg_vec

		self.assertIsNone(aequal(arr, test_mod(f, a=arg_vec).values))

	def test_call_positional_keyword(self):
		def f(s, a, b):
			return np.add(np.divide(s, a), np.divide(a, b))

		arg_vec1 = np.random.random_sample(N)
		arg_vec2 = np.random.random_sample(N)
		arr = self.new_blank()
		arr = (test_arr / arg_vec1) + (arg_vec1 / arg_vec2)

		self.assertIsNone(aequal(arr, test_mod(f, arg_vec1, b=arg_vec2).values))

	def test_dict_str(self):

		diff = self.new_blank()
		diff[1:] = test_arr[1:] - test_arr[:-1]

		mod = test_mod({'foo': 'diff'})
		self.assertIsNone(aequal(diff, mod.values))

	def test_dict_str_n(self):

		mod1 = test_mod({'foo': 'diff'}, n=3)
		mod2 = test_mod({'foo': 'diff', 'n': 3})
		self.assertIsNone(aequal(mod1.values, mod2.values))

	def test_dict_call(self):

		f = lambda s: s - 1
		mod1 = test_mod({'foo': f})
		mod2 = test_mod(f)
		self.assertIsNone(aequal(mod1.values, mod2.values))

	def test_dict_call_positional(self):

		def f(s, bar=0):
			return s - bar
		mod1 = test_mod({'foo': f, 'bar': 2})
		mod2 = test_mod(f, 2)
		self.assertIsNone(aequal(mod1.values, mod2.values))

	def test_dict_call_keyword(self):
		def f(s, bar=0):
			return s + bar
		mod1 = test_mod({'foo': f, 'bar': 2})
		mod2 = test_mod(f, bar=2)
		self.assertIsNone(aequal(mod1.values, mod2.values))

	def test_dict_iter(self):

		arr = np.empty((N, 2))
		arr[:] = np.nan
		arr[1:, 0] = test_arr[1:] - test_arr[:-1]
		arr[:, 1] = test_arr + 1

		f = lambda s, bar: s + bar
		mod = test_mod(['diff', {'func': f, 'bar': 1}])
		self.assertIsNone(aequal(arr, mod.values))


if __name__ == '__main__':
	unittest.main()
