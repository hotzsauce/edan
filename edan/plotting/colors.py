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
		],
		'sequence': [
			['#003f5c', '#4c6a82', '#8699aa', '#c1cbd4'], # blues
			['#ff7c43', '#ffa176', '#ffc2a5', '#ffe1d2'], # oranges
			['#429c55', '#75b57e', '#a4cea7', '#d1e6d2'], # greens
			['#e34d50', '#f17e78', '#fbaaa3', '#ffd5d1'], # reds
			['#a05195', '#b97caf', '#d1a7c9', '#e8d3e4'], # purples
			['#dec64e', '#ead47c', '#f3e2a8', '#faf0d3'], # yellows
			['#f95d6a', '#ff8b8e', '#ffb5b4', '#ffdbd9'], # pinks
			['#4195d3', '#7caede', '#abc8e9', '#d5e3f4']  # light blues
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
		],
		'sequence': [
			['#0f5499', '#5f7bb2', '#96a5cc', '#cad1e5'], # blues
			['#990f3d', '#b85768', '#d48f98', '#ebc6ca'], # reds
			['#9ce5f0', '#b7ecf4', '#d0f2f8', '#e8f9fb'], # light blues
			['#f14c5a', '#fc7f80', '#ffacaa', '#ffd7d5'], # salmons
			['#96cc28', '#b4d967', '#cfe69a', '#e8f2cc'], # greens
			['#593380', '#82639f', '#ac94be', '#d5c9de'], # purples
			['#ff7faa', '#ffa3c0', '#ffc3d5', '#ffe1ea'], # pinks
			['#ccc5b8', '#d9d3c9', '#e5e2db', '#f2f0ed']  # light browns
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
		],
		'sequence': [
			['#066fa1', '#6091b8', '#97b4d0', '#cbd9e7'], # dark blue
			['#2ec1d3', '#78d1de', '#aae0e9', '#d5f0f4'], # cyan
			['#ab8a94', '#c0a6ae', '#d5c3c8', '#eae1e3'], # pale maroon
			['#993e4f', '#b66e77', '#d09da2', '#e9cdd0'], # dark maroon
			['#90bbcf', '#acccdb', '#c8dde7', '#e4eef3'], # sky blue
			['#03959f', '#63afb6', '#9ac9ce', '#cde4e6'], # ocean blue
			['#e2b465', '#ecc68b', '#f4d9b1', '#fbecd8'], # tangerine
			['#f97a1f', '#ff9e5e', '#ffc096', '#ffe0cb']  # orange
		]
	},
	# bloomberg terminal colors
	'bb': {
		'orange': '#f9a003',
		'red': '#90a11a',
		'light_grey': '#b9b6ae',
		'dark_grey': '#5c5b57',
		'text_color': '#f6f3e8',
		'grid_color': '#7b7974',
		'axes_color': '#000000',
		'fig_color': '#000000',
		'cycle': [
			'#ffffff', '#00aeff', '#ff008c', '#ffc400',
			'#ef3d56', '#b3d334', '#b579b3', '#f36532'
		],
		'sequence': [
			['#ffffff', '#c4c4c4', '#8b8b8b', '#575757'], # greys
			['#00aeff', '#76c2ff', '#abd6ff', '#d7eaff'], # light blue
			['#ff008c', '#ff71aa', '#ffa6c7', '#ffd4e3'], # pinks
			['#ffc400', '#ffd466', '#ffe39e', '#fff1d0'], # yellows
			['#ef3d56', '#fb777d', '#ffa7a8', '#ffd4d3'], # reds
			['#b3d334', '#c9de6e', '#dde99f', '#eff4cf'], # limes
			['#b579b3', '#c89ac6', '#dbbbd9', '#edddec'], # purples
			['#f36532', '#fe8d64', '#ffb699', '#ffdbcc']  # oranges
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

		if not hasattr(self, 'sequence'):
			raise TypeError("palette must be initialized with a 'sequence' attribute")

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

	def sequential_cycler(self, n_elems: int = None):
		"""
		create a color cycle when sequential colors are desired; e.g. when
		multiple methods of more than one series are shown on the same graph.
		"""
		partial_seqs = [s for seq in self.sequence for s in seq[:n_elems]]
		return cycler('color', partial_seqs)


palette_cache = [Palette(_edan_palettes['edan'])]
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
	palette : str | dict | Palette | None
		preconfigured palette name, palette specification,  or None. if None, the
		most recently chosen Palette is returned. if string, must be on of `edan`,
		`ft`, `econ`, or `bb`. if a dict or Palette, construct a new Palette
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
		last_palette = palette_cache[-1]
		return last_palette

	elif isinstance(palette, Palette):
		pal = Palette(palette.colors, n_colors)

		_ = palette_cache.pop()
		palette_cache.append(pal)
		return pal

	elif isinstance(palette, str):
		palettes = ('edan', 'ft', 'econ', 'bb')
		if palette not in palettes:
			raise ValueError(f"palette must be one of {', '.join(palettes)}")

		palette_spec = _edan_palettes[palette]
		pal = Palette(palette_spec, n_colors)

		_ = palette_cache.pop()
		palette_cache.append(pal)
		return pal

	elif isinstance(palette, dict):
		pal = Palette(palette, n_colors)

		_ = palette_cache.pop()
		palette_cache.append(pal)
		return pal

	valid_types = ('None', 'Palette', 'str', 'dict')
	raise TypeError(f"palette must be one of {', '.join(valid_types)}")
