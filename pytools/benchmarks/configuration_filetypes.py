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
import json
from pathlib import Path
from pytools.timetools import Timer

folder = Path(__file__).with_name("data")
if not folder.exists():
	folder.mkdir()
small_json_file = folder / "small_dataset.json"
medium_json_file = folder / "medium_dataset.json"
large_json_file = folder / "large_dataset.json"

small_yaml_file = folder / "small_dataset.yaml"
medium_yaml_file = folder / "medium_dataset.yaml"
large_yaml_file = folder / "large_dataset.yaml"


def generate_configuration_files():
	import pandas
	dataset = Path.home() / "Downloads" / "WEOApr2017all.xlsx"

	table = pandas.read_excel(dataset)

	small_table = table[:int(len(table) / 20)]
	medium_table = table[:int(len(table) / 5)]
	large_table = table

	# Generate json
	small_table.to_json(str(small_json_file))
	medium_table.to_json(str(medium_json_file))
	large_table.to_json(str(large_json_file))

	# generate yaml
	small_table = json.loads(small_json_file.read_text())
	medium_table = json.loads(medium_json_file.read_text())
	large_table = json.loads(large_json_file.read_text())

	with small_yaml_file.open('w') as file1:
		yaml.dump(small_table, file1)
	with medium_yaml_file.open('w') as file2:
		yaml.dump(medium_table, file2)
	with large_yaml_file.open('w') as file3:
		yaml.dump(large_table, file3)


def time_json_read(filename: Path):
	json.loads(filename.read_text())


def time_yaml_read(filename: Path):
	yaml.load(filename.open())


if __name__ == "__main__":
	generate_configuration_files()
	timer = Timer()
	print("timing json with {:.2f}MB file".format(medium_json_file.stat().st_size/1024**2))
	timer.timeFunction(time_json_read, medium_json_file)
	print("timing yaml with {:.2f}MB file".format(medium_yaml_file.stat().st_size/1024**2))
	timer.timeFunction(time_yaml_read,medium_yaml_file, loops = 5)
