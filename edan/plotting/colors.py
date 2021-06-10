import matplotlib.pyplot as plt

edan_palettes = {
	# default plot colors
	'edan': ['#003f5c', '#ff7c43', '#429c55', '#e34d50',
			'#a05195', '#dec64e', '#f95d6a', '#4195d3'],
	# financial times colors
	'ft': ['#0f5499', '#990f3d', '#9ce5f0', '#f14c5a',
			'#96cc28', '#593380', '#ff7faa', '#ccc5b8'],
	# economist colors
	'econ': ['#066fa1', '#2ec1d3', '#ab8a94', '#993e4f',
			'#90bbcf', '#03959f', '#e2b465', '#f97a1f']
}

def color_palette(
	palette: str = 'edan'
):
	return edan_palettes[palette]

def contribution_palette(palette: str = ''):
	"""
	retrieve the list of colors for the bars in contribution plots. in those
	plots, the aggregate growth is a line in the first color of the palette,
	and the colors of the bars cycle through all the other colors, never returing
	to that aggregate color

	Parameters
	----------
	palette : str ( = '' )
		if empty string, returns the list of subcomponent colors of the currently
		used color prop_cycle as determined by matplotlib rcParams. otherwise,
		'palette' should be a recognized color palette, and a list of all but the
		first of those colors in that palette will be returned
	"""
	if palette:
		full_palette = edan_palettes[palette]
		return full_palette[1:]

	colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
	return colors[1:]
