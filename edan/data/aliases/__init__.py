"""

"""

import urllib.request as urequest
import json
import pathlib



# url of crosswalks repo & directory name of local crosswalks
git_url = 'https://raw.githubusercontent.com/hotzsauce/crosswalks/main/crosswalks'
warehouse_name = 'warehouse'

warehouse = pathlib.Path(__file__).parent / warehouse_name
warehouse.mkdir(exist_ok=True)


# file names of constructed crosswalks
pceu = 'edan-bea_underlying_pce.json'
gdpd = 'edan-bea-fred_gdp_detail.json'
gdp = 'edan-bea-fred_gdp.json'

def retrieve_from_git(name):
	local_name = warehouse / name
	if local_name.exists():
		pass
	else:
		full_url = '/'.join((git_url, name))
		with urequest.urlopen(full_url) as url:
			data = json.load(url)

		with open(local_name, 'w') as json_file:
			json.dump(data, json_file, indent=4)

retrieve_from_git(pceu)
retrieve_from_git(gdpd)
retrieve_from_git(gdp)



# create funnels for aliases
from edan.data.aliases.mappings import aliases_by_source
alias_maps = {s: aliases_by_source(s) for s in ('fred', 'bea')}
