"""
	Compares the performance of JSON vs YAML.

	Some Runs:
	timing json with 0.55MB file
		13.24ms ± 1.79ms per loop [100 loops][11.07ms, 22.78ms]
	timing yaml with 0.62MB file
		3.61s ± 73.98ms per loop [5 loops][3.50s, 3.69s]

	timing json with 2.27MB file
		50.91ms ± 6.11ms per loop [100 loops][46.41ms, 78.96ms]
	timing yaml with 2.53MB file
		13.99s ± 364.66ms per loop [5 loops][13.32s, 14.40s]
"""

import yaml
import poyo
import json
from pathlib import Path
from pytools.timetools import Timer
import strictyaml

folder = Path(__file__).with_name("data")
if not folder.exists():
	folder.mkdir()
json_small_file = folder / "small_dataset.json"
json_medium_file = folder / "medium_dataset.json"
json_large_file = folder / "large_dataset.json"

yaml_small_file = folder / "small_dataset.yaml"
yaml_medium_file = folder / "medium_dataset.yaml"
yaml_large_file = folder / "large_dataset.yaml"

small_sample = {
	'Hello World':     {
		'madness': 'This is madness',
		'gh': 'https://github.com/{0}.git'
	},
	'NullValue':       None,
	'Yay #python':     'Cool!',
	'default_context': {
		'123':             456.789,
		'doc_tools':     ['mkdocs', 'sphinx', None],
		'docs':          True,
		'email':         'raphael@hackebrot.de',
		'foo':           'hallo #welt',
		'greeting':      'こんにちは',
		'gui':           False,
		'lektor':        '0.0.0.0:5000',
		'relative-root': '/',
		'some:int':      1000000,
		'trueish':       'Falseeeeeee'
	},
	'zZz':             True}
from pprint import pprint

pprint(small_sample)
print("", flush = True)


def generate_configuration_files():
	import pandas
	dataset = Path.home() / "Downloads" / "WEOApr2018all.xlsx"

	table = pandas.read_excel(dataset)

	small_table = small_sample

	# Generate json
	json_small_file.write_text(json.dumps(small_table, indent = 4, sort_keys = True))
	# json_medium_file.write_text(json.dumps(med))
	# large_table.to_json(str(large_json_file))

	# generate yaml
	yaml_small_file.write_text(yaml.dump(small_table, default_flow_style = False))


# with large_yaml_file.open('w') as file3:
#	yaml.dump(large_table, file3)


def time_json_read(filename: Path):
	json.loads(filename.read_text())


def time_yaml_read(filename: Path):
	yaml.load(filename.open())

def time_strictyaml_read(filename: Path):
	strictyaml.load(filename.read_text())

def time_poyo_read(filename: Path):
	poyo.parse_string(filename.read_text())


if __name__ == "__main__":
	generate_configuration_files()
	timer = Timer()

	print("timing json with {:.2f}MB file".format(json_small_file.stat().st_size / 1024 ** 2))
	timer.timeFunction(time_json_read, json_small_file)

	print("timing yaml with {:.2f}MB file".format(yaml_small_file.stat().st_size / 1024 ** 2))
	timer.timeFunction(time_yaml_read, yaml_small_file, loops = 5)

	print("timing syaml with {:.2f}MB file".format(yaml_small_file.stat().st_size / 1024 ** 2))
	timer.timeFunction(time_strictyaml_read, yaml_small_file, loops = 5)

	print("timing poyo with {:.2f}MB file".format(yaml_small_file.stat().st_size / 1024**2))
	timer.timeFunction(time_poyo_read, yaml_small_file)