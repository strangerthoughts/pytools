from setuptools import setup

setup(
	name = 'pytools',
	version = '0.1',
	packages = ['pytools', 'pytools.widgets', 'pytools.geotools', 'pytools.filetools', 'pytools.plottools',
				'pytools.timetools', 'pytools.tabletools', 'pytools.numbertools', 'pytools.systemtools'],
	url = 'https://github.com/Kokitis/pytools',
	license = 'MIT',
	author = 'Chris Deitrick',
	author_email = '',
	description = 'A collection of tools to simplify common tasks.',
	install_requires = ['psutil', 'pandas', 'numpy', 'matplotlib', 'fuzzywuzzy', 'pandas']
)
