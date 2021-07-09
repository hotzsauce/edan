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
			['#003f5c', '#007a9b', '#00bad3', '#1cffff'], # blues
			['#ff7c43', '#fea05a', '#fec07a', '#ffdca1'], # oranges
			['#429c55', '#62bc74', '#82dd94', '#a2ffb5'], # greens
			['#e34d50', '#f07c74', '#f9a69c', '#ffcfc7'], # reds
			['#a05195', '#bf7db8', '#dfa9db', '#ffd6ff'], # purples
			['#dec64e', '#e9d95d', '#f4ec6c', '#ffff7c'], # yellows
			['#f95d6a', '#ff858e', '#ffaab1', '#ffcdd2'], # pinks
			['#4195d3', '#27b9eb', '#32ddf9', '#64ffff']  # light blues
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
			['#066fa1', '#009bff', '#00c6ff', '#8ee9ff'], # dark blue
			['#2ec1d3', '#6fd6e0', '#9ceaef', '#c6ffff'], # cyan
			['#ab8a94', '#c7a9b7', '#e3c9db', '#ffebff'], # pale maroon
			['#993e4f', '#bd687f', '#de94b1', '#ffc1e2'], # dark maroon
			['#90bbcf', '#91d1e3', '#92e8f4', '#97ffff'], # sky blue
			['#03959f', '#4db7be', '#7adbde', '#a5ffff'], # ocean blue
			['#e2b465', '#ebcc81', '#f4e3a0', '#fffac0'], # tangerine
			['#f97a1f', '#f8a851', '#f9cf8a', '#fff1ca']  # orange
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
			['#ffffff', '#c4c4c4', '#b8b8b8', '#575757'], # greys
			['#00aeff', '#1eccff', '#63e7ff', '#9effff'], # light blue
			['#ff008c', '#ff65bc', '#ff98e3', '#ffc4ff'], # pinks
			['#ffc400', '#fcd850', '#fcea81', '#fffaaf'], # yellows
			['#ef3d56', '#fa7781', '#ffa7ac', '#ffd5d7'], # reds
			['#b3d334', '#cde116', '#e5f091', '#fbffbc'], # limes
			['#b579b3', '#cd9bcc', '#e6bee5', '#ffe2ff'], # purples
			['#f36532', '#f69553', '#fabe82', '#ffe3b9']  # oranges
		]
	},
	# international monetary fund colors
	'imf': {
		'light_grey': '#cfd4dd',
		'dark_grey': '#939598',
		'text_color': '#0f0f0f',
		'grid_color': '#ffffff', # no grid on IMF plots
		'axes_color': '#ffffff',
		'fig_color': '#ffffff',
		'cycle': [
			'#0062af', '#c41230', '#387c2b', '#fdbd57',
			'#9b31d0', '#ff8a00', '#19b6d5', '#d378c7'
		],
		'sequence': [
			['#0062af', '#0098d4', '#37ccec', '#8effff'], # blues
			['#c41230', '#dc5c5b', '#f08f8a', '#ffc1bc'], # reds
			['#387c2b', '#5da64b', '#83d26c', '#aaff83'], # greens
			['#fdbd57', '#ffce58', '#ffdf5c', '#fff062'], # yellows
			['#9b31d0', '#c36cde', '#e4a2ed', '#ffd8ff'], # purples
			['#ff8a00', '#feaa2a', '#fec64e', '#ffe173'], # oranges
			['#19b6d5', '#68cfel', '#9be7ee', '#c9ffff'], # light blues
			['#d378c7', '#e19edb', '#f0c3ee', '#ffe7ff']  # pinks
		]
	}
}
palette_names = list(_edan_palettes.keys())



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
		if palette not in palette_names:
			raise ValueError(f"palette must be one of {', '.join(palette_names)}")

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
