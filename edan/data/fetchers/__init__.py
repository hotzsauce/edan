from edan.data.fetchers.fred_fetcher import FredFetcher
from edan.data.fetchers.av_fetcher import AlphaVantageFetcher
from edan.data.fetchers.bea_fetcher import BeaFetcher

from edan.data.fetchers.base import EdanFetcher

fetchers_by_source = {}
def add_source(source, api):
	try:
		_api = api()
		fetchers_by_source[source] = _api
	except KeyError:
		# api key was not saved
		pass
add_source('fred', FredFetcher)
add_source('av', AlphaVantageFetcher)
add_source('bea', BeaFetcher)
