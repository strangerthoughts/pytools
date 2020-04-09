from setuptools import setup

setup(
	name = 'infotools',
	version = '0.5.2',
	packages = ['infotools', 'infotools.timetools', 'infotools.timetools'],
	url = 'https://github.com/Kokitis/infotools',
	license = 'MIT',
	author = 'proginoskes',
	author_email = 'chrisdeitrick1@gmail.com',
	description = 'A collection of tools to make common tasks simpler.',
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	], install_requires = ['pendulum', 'fuzzywuzzy', 'loguru', 'psutil', 'pandas', 'tqdm'],
	tests_requires = ['pytest']
)
