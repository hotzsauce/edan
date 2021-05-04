import pathlib
from setuptools import setup


cwd = pathlib.Path(__file__).parent
long_description = (cwd / 'README.md').read_text()

setup(
	name = 'edan',
	packages = ['edan'],
	description = (
		"economic data analysis toolkit, with an emphasis on  NIPA/PCE accounts"
	),
	version = '0.1',
	license = 'MIT',
	long_description_content_type = 'text/markdown',
	long_description = long_description,
	author = 'hotzsauce',
	author_email = 'githotz@gmail.com',
	url = 'https://www.github.com/hotzsauce/edan-dev',
	keywords = ['economics', 'econ', 'nipa', 'pce', 'gdp', 'treasuries'],
	install_requires = [
		'numpy',
		'pandas',
		'pyarrow',
		'matplotlib',
		'fredapi',
		'beapy',
		'funnelmap'
	],
	include_package_data = True,
	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.7'
	]
)
