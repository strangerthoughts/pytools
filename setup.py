from setuptools import setup
"""
python setup.py sdist bdist_wheel
twine upload -repository pypi dist/*
"""

import infotools
if infotools.DEBUG:
	message = f"The module is still in debug mode!"
	raise ValueError(message)

setup(
	name = 'infotools',
	version = '0.7',
	packages = ['infotools', 'infotools.timetools', 'infotools.numbertools'],
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
