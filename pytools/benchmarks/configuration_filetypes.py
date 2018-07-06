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
import hjson
import toml
from pathlib import Path
from pytools.timetools import Timer
import strictyaml
from typing import Dict
import datetime

folder = Path(__file__).with_name("data")
if not folder.exists():
	folder.mkdir()
json_small_file = folder / "small_dataset.json"
json_medium_file = folder / "medium_dataset.json"
json_large_file = folder / "large_dataset.json"

hjson_small_file = folder / "small_dataset.hjson"
toml_small_file = folder / "small_dataset.toml"

yaml_small_file = folder / "small_dataset.yaml"
yaml_medium_file = folder / "medium_dataset.yaml"
yaml_large_file = folder / "large_dataset.yaml"

small_sample = {
	'Hello World':     {
		'madness': 'This is madness',
		'gh':      'https://github.com/{0}.git'
	},
	'NullValue':       None,
	'Yay #python':     'Cool!',
	'default_context': {
		'123':           456.789,
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
	'zZz':             True,
	'pythonTypes':     {
		'a': ('a', 'b', 'c', 1, 2, 3),
		# 'b': {'a', 'a', 'a', 2, 2, 2},
		#'c': datetime.datetime.now()
	}
}


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


def time_json_write(data: Dict, filename: Path) -> Path:
	filename.write_text(json.dumps(data, indent = 4, sort_keys = True))
	return filename


def time_hjson_write(data: Dict, filename: Path) -> Path:
	filename.write_text(hjson.dumps(data))
	return filename


def time_toml_write(data: Dict, filename: Path) -> Path:
	filename.write_text(toml.dumps(data))
	return filename


def time_yaml_write(data: Dict, filename: Path) -> Path:
	yaml_string = yaml.dump(data, default_flow_style = False)
	filename.write_text(yaml_string)
	return filename


def time_yaml_cdump_write(data: Dict, filename: Path) -> Path:
	yaml_string = yaml.dump(data, default_flow_style = False, Dumper = yaml.CDumper)
	filename.write_text(yaml_string)
	return filename


# print(yaml.safe_dump(json.loads(json.dumps(small_sample))))
#print(yaml.safe_dump(small_sample))
if __name__ == "__main__":
	generate_configuration_files()
	timer = Timer()
	sample = json.loads(json.dumps(small_sample))
	json_filename = time_json_write(sample, json_small_file)
	hjson_filename = time_hjson_write(sample, hjson_small_file)
	toml_filename = time_toml_write(sample, toml_small_file)
	yaml_filename = time_yaml_write(sample, yaml_small_file)

	json_contents = json_filename.read_text()
	hjson_contents = hjson_filename.read_text()
	yaml_contents = yaml_filename.read_text()

	print("timing json write")
	timer.timeFunction(time_json_write, sample, json_small_file)
	print()

	print("timing hjson write")
	timer.timeFunction(time_hjson_write, sample, hjson_filename)
	print()

	print("timing toml write")
	timer.timeFunction(time_toml_write, sample, toml_filename)
	print("timing yaml write")

	print("pyyaml")
	timer.timeFunction(time_yaml_write, sample, yaml_small_file)
	print("pyyaml cDumper")
	timer.timeFunction(time_yaml_cdump_write, sample, yaml_small_file)
	print()

	print("timing json with {:.2f}MB file".format(json_filename.stat().st_size / 1024 ** 2))
	timer.timeFunction(json.loads, json_contents)
	print()

	print("timing hjson with {:.2f}MB file".format(hjson_filename.stat().st_size / 1024 ** 2))
	timer.timeFunction(hjson.loads, hjson_contents)
	print()

	print("timing yaml with {:.2f}MB file".format(yaml_filename.stat().st_size / 1024 ** 2))
	print("pyyaml")
	timer.timeFunction(yaml.load, yaml_contents)

	print("pyyaml cloader")
	timer.timeFunction(yaml.load, yaml_contents, Loader = yaml.CLoader, loops = 100)

	print("strictyaml")
	timer.timeFunction(strictyaml.load, yaml_contents)

	print("poyo".format(yaml_small_file.stat().st_size / 1024 ** 2))
	timer.timeFunction(poyo.parse_string, yaml_contents)
