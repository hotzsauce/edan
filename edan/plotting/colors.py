import matplotlib.pyplot as plt

edan_palettes = {
	'edan': ['#003f5c', '#ff7c43', '#429c55', '#e34d50',
			'#a05195', '#dec64e', '#f95d6a', '#4195d3'],
	'edan_contr': ['#ff7c43', '#429c55', '#e34d50',
			'#a05195', '#dec64e', '#f95d6a', '#4195d3']
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
