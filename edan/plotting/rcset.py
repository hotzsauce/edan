"""
plot style & scaling
"""
import matplotlib as mpl
from cycler import cycler

import edan.plotting.colors as colors

__all__ = ['set_theme']

_style_params = [
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
	'xtick.direction', # one of {'out', 'in', 'inout'}
	'ytick.direction',
	'lines.solid_capstyle', # handling outer corners when lines change directions

	'image.cmap', # unsure
	'font.family', # {'sans-serif', 'serif', 'cursive', 'fantasy', 'monospace'}
	'font.sans-serif',

	'xtick.bottom', # draw ticks on each spline
	'xtick.top',
	'ytick.left',
	'ytick.right',

	'axes.spines.left' # borders around each axis
	'axes.spine.bottom',
	'axes.spine.right',
	'axes.spine.top'
]

_axes_params = [
	'font.size',
	'axes.labelsize',
	'axes.titlesize',
	'xtick.labelsize',
	'ytick.labelsize',
	'legend.fontsize',
	'legend.title_fontsize',

	'axes.linewidth',
	'grid.linewidth',
	'lines.linewidth',
	'lines.markersize',
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


def set_palette(palette=None):
	color = colors.color_palette(palette)
	cycle = cycler('color', color)
	mpl.rcParams['axes.prop_cycle'] = cycle


def set_style(style=None):
	if style is None:
		style_dict = {k: mpl.rcParams[k] for k in _style_params}

	else:
		styles = ['light', 'lightgrid', 'ft', 'econ']
		if style not in styles:
			raise ValueError(f"style must be one of {', '.join(styles)}")

		light_grey = '#85929e'
		dark_grey = '#212f3c'

		# shared style params
		style_dict = {
			'figure.facecolor': 'white',
			'axes.labelcolor': dark_grey,

			'xtick.direction': 'out',
			'ytick.direction': 'out',
			'xtick.color': dark_grey,
			'ytick.color': dark_grey,

			'axes.axisbelow': True,

			'text.color': dark_grey,
			'font.family': ['sans-serif'],
			'font.sans-serif': ['Tahoma', 'sans-serif'],

			'lines.solid_capstyle': 'round',

			'image.cmap': 'magma',

			'xtick.top': False,
			'ytick.right': False,
		}

		if 'grid' in style:
			style_dict.update({
				'axes.grid': True,

				'axes.spines.left': False,
				'axes.spines.bottom': False,
				'axes.spines.right': False,
				'axes.spines.top': False,
			})
		else:
			style_dict.update({
				'axes.grid': False,

				'axes.spines.left': True,
				'axes.spines.bottom': True,
				'axes.spines.right': True,
				'axes.spines.top': True,
			})

		if style.startswith('light'):
			style_dict.update({
				'grid.color': 'white',
				'grid.linestyle': ':',
				'axes.grid.axis': 'both',

				'axes.facecolor': '#e5f1ff',
				'axes.edgecolor': 'white'
			})

		elif style == 'ft':
			ft_light_grey = '#c7c7c7'
			ft_dark_grey = '#66605c'
			ft_paper = '#f2dfce'

			style_dict.update({
				'lines.linewidth': 2.5,

				'axes.grid.axis': 'y',
				'axes.grid': True,

				'axes.spines.left': False,
				'axes.spines.top': False,
				'axes.spines.right': False,

				'axes.edgecolor': ft_dark_grey,

				'grid.linestyle': '-',
				'grid.color': ft_light_grey,

				'axes.facecolor': ft_paper,
				'figure.facecolor': ft_paper,

				'ytick.left': False,
				'ytick.labelcolor': ft_dark_grey,

				'xtick.color': ft_dark_grey,
				'xtick.labelcolor': ft_dark_grey,

				'text.color': '#000000',
			})

		elif style == 'econ':
			econ_light_blue = '#d7e6ef'
			econ_red = '#e3210b'

			econ_dark_grey = '#121317'
			econ_light_grey = '#b2c0c9'

			style_dict.update({
				'lines.linewidth': 2,

				'axes.grid.axis': 'y',
				'axes.grid': True,

				'axes.spines.left': False,
				'axes.spines.top': False,
				'axes.spines.right': False,

				'axes.edgecolor': econ_dark_grey,

				'grid.linestyle': '-',
				'grid.color': econ_light_grey,

				'axes.facecolor': econ_light_blue,

				'ytick.left': False,
				'ytick.labelcolor': econ_dark_grey,

				'xtick.color': econ_dark_grey,
				'xtick.labelcolor': econ_dark_grey,

				'text.color': '#000000'
			})

	mpl.rcParams.update(style_dict)

def set_theme(style='lightgrid', palette='edan', *args, **kwargs):
	set_style(style)
	set_palette(palette)

set_theme()
