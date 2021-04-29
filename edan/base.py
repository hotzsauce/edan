"""
abstract base class for edan objects
"""

from copy import deepcopy


class EdanObject(object):

	def __deepcopy__(self, memo):
		"""create copies of edan custom classes"""
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result

		for k, v in self.__dict__.items():
			setattr(result, k, deepcopy(v, memo))

		return result
