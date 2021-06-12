import matplotlib as mpl
from cycler import cycler

_edan_palettes = {
	# default plot colors
	'edan': {
		'light_grey': '#85929e',
		'dark_grey': '#212f3c',
		'text_color': '#212f3c',
		'grid_color': '#ffffff',
		'axes_color': '#e5f1ff',
		'fig_color': '#ffffff',
		'cycle': [
			'#003f5c', '#ff7c43', '#429c55', '#e34d50',
			'#a05195', '#dec64e', '#f95d6a', '#4195d3'
		]
	},
	# financial times colors
	'ft': {
		'light_grey': '#c7c7c7',
		'dark_grey': '#212f3c',
		'text_color': '#000000',
		'grid_color': '#c7c7c7',
		'axes_color': '#f2dfce',
		'fig_color': '#f2dfce',
		'cycle': [
			'#0f5499', '#990f3d', '#9ce5f0', '#f14c5a',
			'#96cc28', '#593380', '#ff7faa', '#ccc5b8'
		]
	},
	# economist colors
	'econ': {
		'red': '#e3210b', # that iconic red color
		'light_grey': '#b2c0c9',
		'dark_grey': '#121317',
		'text_color': '#000000',
		'grid_color': '#b2c0c9',
		'axes_color': '#d7e6ef',
		'fig_color': '#ffffff',
		'cycle': [
			'#066fa1', '#2ec1d3', '#ab8a94', '#993e4f',
			'#90bbcf', '#03959f', '#e2b465', '#f97a1f'
		]
	}
}


class Palette(object):
	"""set the color palette in a `with` statement"""

	def __init__(self, colors, n_colors=None):

		self.colors = colors
		for color_name, hex_code in self.colors.items():
			# hex code might be an actual hex code, or a sequence of them
			setattr(self, color_name, hex_code)

		if not hasattr(self, 'cycle'):
			raise TypeError("palette must be initialized with a 'cycle' attribute")

		if n_colors is not None:
			self.cycle = self.cycle[:n_colors]

		# iterating over the colors in 'cycle'
		self.idx = 0

	def __enter__(self):
		# print(mpl.rcParams['axes.prop_cycle'].by_key()['color'])
		from edan.plotting.rcset import set_palette

		self._orig_palette = color_palette()
		set_palette(self)
		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		from edan.plotting.rcset import set_palette
		set_palette(self._orig_palette)

	def __len__(self):
		return len(self.cycle)

	def __iter__(self):
		return self

	def __next__(self):
		self.idx += 1
		try:
			return self.cycle[self.idx-1]
		except IndexError:
			self.idx = 0
			raise StopIteration

	def __getitem__(self, idx):
		return self.cycle[self.idx]

	def cycler(self, n_colors: int = None):
		"""
		create a color cycler based on the first `n_colors` colors of the
		`cycle` attribute
		"""
		if n_colors is None:
			return cycler('color', self.cycle)
		return cycler('color', self.cycle[:n_colors])

	def contribution_cycler(self, n_colors: int = None):
		"""
		create a color cycle of all but the first color in the current cycle,
		up to the (n_colors-1)-th color in that cycle
		"""
		if n_colors is None:
			contr_colors = self.cycle[1:]
			return cycler('color', contr_colors)
		return cycler('color', self.cycle[1:n_colors-1])


def color_palette(
	palette: str = None,
	n_colors: int = None,
	desat: float = None,
	as_cmap: bool = False
):
	"""
	choose one of the preconfigured edan palettes

	Parameters
	----------
	palette : str | None
		preconfigured palette name, or None. if None, a palette with the current
		cycle & the other default `edan` colors is returned. if string, must be
		one of `edan`, `ft`, or `econ`
	n_colors : int ( = None )
		number of colors in the cycle. the default number depends on the format of
		`palette`
	desat : float ( = None )
		proportion to desaturate each color by

	Returns
	-------
	palette : Palette
	"""
	if as_cmap:
		raise NotImplementedError("as_cmap")

	if palette is None:
		edan_colors = _edan_palettes['edan'].copy()

		cycler = mpl.rcParams['axes.prop_cycle']
		edan_colors['cycle'] = cycler.by_key()['color']
		return Palette(edan_colors, n_colors)

	elif isinstance(palette, Palette):
		return Palette(palette.colors, n_colors)

	elif isinstance(palette, str):
		palettes = ('edan', 'ft', 'econ')
		if palette not in palettes:
			raise ValueError(f"palette must be one of {', '.join(palettes)}")

		palette_spec = _edan_palettes[palette]
		return Palette(palette_spec, n_colors)

	valid_types = ('None', 'Palette', 'str')
	raise TypeError(f"palette must be one of {', '.join(valid_types)}")
