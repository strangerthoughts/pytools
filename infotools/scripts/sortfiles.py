# Sort by size, filetype, etc.

from pathlib import Path
from typing import List, Dict

def get_all_files(folder:Path)->List[Path]:
	return list(folder.glob("**/*")) # Is a list because it will likely be used more than once.


def sort_files(source:Path, destination:Path, by:str):
	pass

def sort_images_by_size(images:List[Path])->Dict[str,List[Path]]:
	pass

def sort_files_by_type(files:List[Path])->Dict[str,List[Path]]:
	filetype_index: Dict[str, List[Path]] = dict()

	for filename in files:
		suffix = filename.suffix

		if suffix in filetype_index:
			filetype_index[suffix].append(filename)
		else:
			filetype_index[suffix] = [filename]
	return filetype_index

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()

	parser.add_argument(
		"--by",
		help = "The attribute to group files by. {}",
		type = str,
		default = 'imageSize'
	)

	parser.add_argument(
		"--source",
		help = "The source folder to sort.",
		type = Path
	)

	parser.add_argument(
		"--destination",
		help = "The location where the output files should go. Defaults to the source folder."
	)

	args = parser.parse_args()

	if args.destination is None: args.destination = args.source

