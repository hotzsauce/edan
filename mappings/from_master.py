"""
creating mappings and registry from the master JSON
"""

import json

with open('master_registry.json', 'r') as json_file:
	master = json.load(json_file)

def create_registry(file_name='.registry.json'):

	registry = []
	for entry in master:
		reg = {
			'code': entry['code'],
			'__concept__': entry['__concept__'],
			'__table__': entry['__table__'],
			'__level__': entry['__level__'],
			'__ctype__': entry['__ctype__'],
			'quantity': entry['quantity'],
			'price': entry['price'],
			'nominal': entry['nominal'],
			'real': entry['real'],
			'nominal_level': entry['nominal_level'],
			'real_level': entry['real_level'],
			'empl_level': entry['empl_level'],
			'empl_level_nsa': entry['empl_level_nsa'],
			'long_name': entry['long_name'],
			'short_name': entry['short_name'],
			'source': entry['source'],
		}
		registry.append(reg)

	with open(file_name, 'w') as json_file:
		json.dump(registry, json_file, indent=4)


def create_alias_mapping(
	file_name='edan-bea_underlying_pce.json',
	sources=['bea'],
	concept='nipa',
	table='gdp',
	how=all
):

	sources_edan = ['edan', 'edan_simple'] + sources

	aliases = {}
	for entry in master:
		ec, et = entry['__concept__'], entry['__table__']
		if how((ec == concept, et == table)):
			mapping = {
				'long_name': entry['long_name'],
				'__row__': entry['__row__'],
				'__level__': entry['__level__']
			}
			for meas, codes in entry['measures'].items():
				selected = {s: codes[s] for s in sources}
				if any(selected.values()):
					mapping[meas] = {s: codes[s] for s in sources_edan}

			aliases[entry['code']] = mapping

	with open(file_name, 'w') as json_file:
		json.dump(aliases, json_file, indent=4)


if __name__ == '__main__':

	create_registry()
	create_alias_mapping('edan-bea_underlying_pce.json', ['bea'], 'nipa', 'pce')
	create_alias_mapping('edan-bea-fred_gdp.json', ['bea', 'fred'], 'nipa', 'gdp')
	create_alias_mapping('edan-bea-fred_gdp_detail.json', ['bea', 'fred'], 'nipa', 'gdp')
	create_alias_mapping('edan-bls_cpi_detail.json', ['bls'], 'cpi', 'cpi')
	create_alias_mapping('edan-bls_ces_detail.json', ['bls'], 'ces', 'ces')
