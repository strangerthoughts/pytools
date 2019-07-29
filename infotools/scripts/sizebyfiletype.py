"""
	This scripts gives the total space occupied per filetype
"""
from pathlib import Path 

def sizebyfiletype(folder:Path):

	all_filenames = folder.glob("**/*")
	data = dict()
	for filename in all_filenames:
		if filename.is_dir(): continue

		filesize = filename.stat().st_size
		filetype = filename.suffix

		if filetype not in data:
			data[filetype] = 0
		data[filetype] += filesize

	return data

def save_data(data, filename:Path):
	with filename.open('w') as file1:
		file1.write("filetype\tsize\n")
		for filetype, size in data.items():
			file1.write(f"{filetype}\t{size}\n")


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()

	parser.add_argument(
		"folder",
		help = "The folder to search through",
		type = Path
	)

	parser.add_argument(
		"-o", "--output",
		help = "The tsv file to save the output to.",
		type = Path,
		dest = "output",
		action = "store"
	)

	args = parser.parse_args()

	d = sizebyfiletype(args.folder)
	if args.output:
		save_data(d, args.filename)
	else:
		for filetype, size in sorted(d.items(), key = lambda s: s[1], reverse = True):
			s = size / 1024**2
			print(f"{filetype}\t{s:.2f}MB")
