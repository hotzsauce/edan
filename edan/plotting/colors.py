edan_palettes = {
	'edan': ['#003f5c', '#ff7c43', '#429c55', '#e34d50',
			'#a05195', '#dec64e', '#f95d6a', '#4195d3']
}


def color_palette(
	palette: str = 'edan'
):
	return edan_palettes[palette]
