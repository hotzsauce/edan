"""
plot style & scaling

a near-carbon copy of seaborn.rcmod; basically the only alterations are the
default settings for the RCParams. classes & functions here are identical
to seaborn's. many thanks to the developers there
"""
import warnings
import functools
import matplotlib as mpl
from cycler import cycler

from edan.plotting.colors import (
	color_palette,
	palette_names
)

__all__ = [
	'set_theme',
	'reset_defaults',
	'axes_style',
	'set_style',
	'plotting_context',
	'set_context',
	'set_palette'
]

_style_keys = [
	'axes.facecolor', # color of the plotting area
	'axes.edgecolor',
	'axes.grid', # True or False
	'axes.grid.axis', # horizontal and/or vertical grid lines
	'axes.axisbelow', # paint axes below patches, lines, etc.
	'axes.labelcolor', # color of x- and y-axis labels

	'figure.facecolor', # color of area outside of axes

	'grid.color',
	'grid.linestyle', # one of {'-', '--', '-.', '.', ''}

	'text.color', # color of all text on axes

	'xtick.color', # color of tick marks on axes
	'ytick.color',
	'xtick.labelcolor', # color of text on axes
	'ytick.labelcolor',
	'xtick.direction', # one of {'out', 'in', 'inout'}
	'ytick.direction',

	'xtick.bottom', # draw ticks on each spine
	'xtick.top',
	'ytick.left',
	'ytick.right',

	'lines.solid_capstyle', # handling outer corners when lines change directions
	'lines.linewidth', # linewidth & marker are in seaborn's context keys
	'lines.markersize',

	'patch.edgecolor',
	'patch.force_edgecolor',

	'image.cmap', # unsure
	'font.family', # {'sans-serif', 'serif', 'cursive', 'fantasy', 'monospace'}
	'font.sans-serif',

	'axes.spines.left', # borders around each axis
	'axes.spines.bottom',
	'axes.spines.right',
	'axes.spines.top'
]

_context_keys = [
	'font.size',
	'axes.labelsize',
	'axes.titlesize',
	'xtick.labelsize',
	'ytick.labelsize',
	'legend.fontsize',
	'legend.title_fontsize',

	'axes.linewidth',
	'grid.linewidth',
	'patch.linewidth',

	'xtick.major.width',
	'ytick.major.width',
	'xtick.minor.width',
	'ytick.minor.width',

	'xtick.major.size',
	'ytick.major.size',
	'xtick.minor.size',
	'ytick.minor.size',
]


def set_theme(
	context='notebook',
	style='edan',
	palette='',
	font='sans-serif',
	font_scale=1,
	color_codes=False,
	rc=None
):
	"""
	set aspects of the visual theme for all matplotlib and edan plots

	this function changes the global defaults for all plots using the matplotlib
	rcParams system. the themeing is decomposed into several distinct sets of
	parameter values

	Parameters
	----------
	context : str | dict ( = 'notebook' )
		scaling parameters
	style : str | dict ( = 'edan' )
		axes style parameters
	palette : str | sequence ( = '' )
		color palette. if not provided, use `style`'s palette
	font : str ( = 'sans-serif' )
		font family, see matplotlib font manager
	font_scale : float | int ( = 1 )
		separate scaling factor to independently scale the size of the font elements
	color_codes : bool ( = True )
		if `True` and `palette` is an edan palette remap the shorthand color codes
		(e.g. 'b', 'g', 'r', etc.) to the colors from this palette
	rc : dict | None ( = None )
		dictionary of rc parameters to override the above
	"""
	set_context(context, font_scale)
	set_style(style, rc={'font.family': font})
	if palette:
		set_palette(palette, color_codes=color_codes)
	else:
		set_palette(style, color_codes=color_codes)
	if rc is not None:
		mpl.rcParams.update(rc)


def reset_defaults():
	"""restore all rc params to default settings"""
	mpl.rcParams.update(mpl.rcParamsDefault)


def axes_style(
	style=None,
	rc=None
):
	"""
	get the parameters that control the general style of the plots.

	the style parameters control properties like the color of the background and
	whether a grid is enable by default. this is accomplished using the rcParams
	system

	this function can also be used as a context manager to temporarily alter the
	global defaults.

	Parameters
	----------
	style : None, dict, or one of {'edan', 'ft', 'econ', 'bb', 'imf'} ( = None )
		a dictionary of parameters or the name of a preconfigured style
	rc : dict ( = None )
		parameter mappings to override the values in the preset edan style
		dictionaries. this only updates parameters that are considered part
		of the style definition
	"""

	if style is None:
		style_dict = {k: mpl.rcParams[k] for k in _style_keys}

	elif isinstance(style, dict):
		style_dict = style

	else:
		if style not in palette_names:
			raise ValueError(f"style must be one of {', '.join(palette_names)}")

		# shared style params
		style_dict = {
			'axes.grid': True,
			'axes.axisbelow': True,

			'xtick.direction': 'out',
			'ytick.direction': 'out',

			'xtick.bottom': True,
			'xtick.top': False,
			'ytick.right': False,

			'font.family': ['sans-serif'],
			'font.sans-serif': ['Tahoma', 'sans-serif'],

			'axes.spines.left': False,
			'axes.spines.bottom': False,
			'axes.spines.right': False,
			'axes.spines.top': False
		}

		if style == 'edan':
			palette = color_palette('edan')
			style_dict.update({
				'axes.facecolor': palette.axes_color,
				'axes.labelcolor': palette.dark_grey,

				'axes.grid.axis': 'both',
				'grid.color': palette.grid_color,
				'grid.linestyle': ':',

				'figure.facecolor': palette.fig_color,

				'text.color': palette.text_color,

				'xtick.color': palette.dark_grey,
				'ytick.color': palette.dark_grey,
				'xtick.labelcolor': palette.dark_grey,
				'ytick.labelcolor': palette.dark_grey,

				'ytick.left': True,

				'lines.linewidth': 1.5,
				'lines.markersize': 6
			})
			set_palette('edan')

		elif style == 'ft':
			palette = color_palette('ft')
			style_dict.update({
				'axes.facecolor': palette.axes_color,
				# 'axes.edgecolor': palette.dark_grey,
				'axes.labelcolor': palette.dark_grey,

				# pandas issue 17725
				'axes.grid.axis': 'y',
				'grid.color': palette.grid_color,
				'grid.linestyle': '-',

				'figure.facecolor': palette.fig_color,

				'text.color': palette.text_color,

				'xtick.color': palette.dark_grey,
				'ytick.color': palette.dark_grey,
				'xtick.labelcolor': palette.dark_grey,
				'ytick.labelcolor': palette.dark_grey,

				'ytick.left': True,

				'lines.linewidth': 2.5,
				'lines.markersize': 9
			})
			set_palette('ft')

		elif style == 'econ':
			palette = color_palette('econ')
			style_dict.update({
				'axes.facecolor': palette.axes_color,
				# 'axes.edgecolor': palette.dark_grey,
				'axes.labelcolor': palette.dark_grey,

				# pandas issue 17725
				'axes.grid.axis': 'y',
				'grid.color': palette.grid_color,
				'grid.linestyle': '-',

				'figure.facecolor': palette.fig_color,

				'text.color': palette.text_color,

				'xtick.color': palette.dark_grey,
				'ytick.color': palette.dark_grey,
				'xtick.labelcolor': palette.dark_grey,
				'ytick.labelcolor': palette.dark_grey,

				'ytick.left': False,

				'lines.linewidth': 2,
				'lines.markersize': 8
			})
			set_palette('econ')

		elif style == 'bb':
			palette = color_palette('bb')
			style_dict.update({
				'axes.facecolor': palette.axes_color,
				# 'axes.edgecolor': palette.dark_grey,
				'axes.labelcolor': palette.light_grey,

				'axes.grid.axis': 'both',
				'grid.color': palette.grid_color,
				'grid.linestyle': ':',

				'figure.facecolor': palette.fig_color,

				'text.color': palette.text_color,

				'xtick.color': palette.light_grey,
				'ytick.color': palette.light_grey,
				'xtick.labelcolor': palette.light_grey,
				'ytick.labelcolor': palette.light_grey,

				'ytick.left': True,

				'lines.linewidth': 1.5,
				'lines.markersize': 6
			})
			set_palette('bb')

		elif style == 'imf':
			palette = color_palette('imf')
			style_dict.update({
				'axes.facecolor': palette.axes_color,
				'axes.labelcolor': palette.text_color,

				'axes.grid': False,

				'figure.facecolor': palette.fig_color,

				'text.color': palette.text_color,

				'xtick.color': palette.dark_grey,
				'ytick.color': palette.dark_grey,
				'xtick.labelcolor': palette.dark_grey,
				'ytick.labelcolor': palette.dark_grey,

				'ytick.left': True,
				'ytick.right': True,

				'lines.linewidth': 1.5,
				'lines.markersize': 6
			})
			set_palette('imf')


	if rc is not None:
		style_dict.update(rc)

	# wrap in an _AxesStyle object so this can be used in a `with` statement
	style_object = _AxesStyle(style_dict)

	return style_object


def set_style(
	style=None,
	rc=None
):
	"""
	get the parameters that control the general style of the plots.

	the style parameters control properties like the color of the background and
	whether a grid is enable by default. this is accomplished using the rcParams
	system

	this function can also be used as a context manager to temporarily alter the
	global defaults.

	Parameters
	----------
	style : None, dict, or one of {'edan', 'ft', 'econ'} ( = None )
		a dictionary of parameters or the name of a preconfigured style
	rc : dict ( = None )
		parameter mappings to override the values in the preset edan style
		dictionaries. this only updates parameters that are considered part
		of the style definition
	"""
	style_object = axes_style(style, rc)
	mpl.rcParams.update(style_object)


def plotting_context(context=None, font_scale=1, rc=None):
	"""
	get the parameters that control the scaling of plot elements

	this affects things like the size of the labels, lines, and other elements of
	the plot, but not the overall style. this is accomplished using the rcParams
	system

	the base context is 'notebook', and the other contexts are 'paper', 'talk',
	and 'poster', which are versions of the notebook parameters scaled by different
	values. font elements can also be scaled independently of (but relative to)
	the other values

	this function can also be used as a context manager to temporarily alter the
	global defaults.

	Parameters
	----------
	context : None | dict | {paper, notebook, talk, poster}
		a dictionary of parameters or the name of a preconfigured set
	font_scale : float ( = 1 )
		separate scaling factor to independently scale the size of the the font
		elements
	rc : dict ( = None )
		parameter mappings to override the values in the present seaborn context
		dictionaries. this only updates parameters that are considered part of
		the context definition
	"""
	if context is None:
		context_dict = {k: mpl.rcParams[k] for k in _context_keys}

	elif isinstance(context, dict):
		context_dict = context

	else:

		contexts = ('paper', 'notebook', 'talk', 'poster')
		if context not in contexts:
			raise ValueError(f"context must be in {', '.join(contexts)}")

		# set up dictionary of default parameters
		texts_base_context = {
			'font.size': 10,
			'axes.labelsize': 12,
			'axes.titlesize': 12,
			'xtick.labelsize': 11,
			'ytick.labelsize': 11,
			'legend.fontsize': 11,
			'legend.title_fontsize': 12
		}

		base_context = {
			'axes.linewidth': 1.25,
			'grid.linewidth': 1,
			'lines.linewidth': 1.5,
			'lines.markersize': 6,
			'patch.linewidth': 1,

			'xtick.major.width': 1.25,
			'ytick.major.width': 1.25,
			'xtick.minor.width': 1,
			'ytick.minor.width': 1,

			'xtick.major.size': 6,
			'ytick.major.size': 6,
			'xtick.minor.size': 4,
			'ytick.minor.size': 4
		}
		base_context.update(texts_base_context)

		# scale all the parameters by the same factor depnding on the context
		scaling = dict(paper=0.8, notebook=1, talk=1.5, poster=2)[context]
		context_dict = {k: v * scaling for k, v in base_context.items()}

		# independently scale the fonts
		font_keys = texts_base_context.keys()
		font_dict = {k: context_dict[k] * font_scale for k in font_keys}
		context_dict.update(font_dict)

	# override these settings with the provided rc dictionary
	if rc is not None:
		context_dict.update(rc)

	# wrap in a _PlottingContext object so this can be used in a with statement
	context_object = _PlottingContext(context_dict)

	return context_object


def set_context(context=None, font_scale=1, rc=None):
	"""
	set the parameters that control the scaling of plot elements

	this affects things like the size of the labels, lines, and other elements of
	the plot, but not the overall style. this is accomplished using the rcParams
	system

	the base context is 'notebook', and the other contexts are 'paper', 'talk',
	and 'poster', which are versions of the notebook parameters scaled by different
	values. font elements can also be scaled independently of (but relative to)
	the other values

	this function can also be used as a context manager to temporarily alter the
	global defaults.

	Parameters
	----------
	context : None | dict | {paper, notebook, talk, poster}
		a dictionary of parameters or the name of a preconfigured set
	font_scale : float ( = 1 )
		separate scaling factor to independently scale the size of the the font
		elements
	rc : dict ( = None )
		parameter mappings to override the values in the present seaborn context
		dictionaries. this only updates parameters that are considered part of
		the context definition
	"""

	context_object = plotting_context(context, font_scale, rc)
	mpl.rcParams.update(context_object)


class _RCAesthetics(dict):

	def __enter__(self):
		rc = mpl.rcParams
		self._orig = {k: rc[k] for k in self._keys}
		self._set(self)

	def __exit__(self, exc_type, exc_value, exc_tb):
		self._set(self._orig)

	def __call__(self, func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			with self:
				return func(*args, **kwargs)
		return wrapper


class _AxesStyle(_RCAesthetics):
	"""light wrapper on a dict to set style temporarily"""
	_keys = _style_keys
	_set = staticmethod(set_style)


class _PlottingContext(_RCAesthetics):
	"""light wrapper on a dict to set context temporarily"""
	_keys = _context_keys
	_set = staticmethod(set_context)


def set_palette(
	palette,
	n_colors=None,
	desat=None,
	color_codes=False
):
	"""
	set the matplotlib color cycle using an edan palette

	Parameters
	----------
	palette : edan color palette | matplotlib color map
		palette definition. should be something that `color_palette` can process
	n_colors : int ( = None )
		number of colors in the cycle. the default number depends on the format
		of `palette`
	desat : float ( = None )
		proportion to desaturate each color by
	color_codes : bool ( = False )
		if `True` and `palette` is an edan palette, remap the shorthand color
		codes (e.g. 'b', 'g', 'r', etc.) to the colors from this palette
	"""
	if color_codes:
		raise NotImplementedError('color_codes')

	palette = color_palette(palette, n_colors, desat)
	mpl.rcParams['axes.prop_cycle'] = palette.cycler()
	mpl.rcParams['patch.facecolor'] = palette[0]
