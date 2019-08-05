# Sort by size, filetype, etc.

from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import mimetypes


def get_all_files(folder: Path) -> List[Path]:
	return list(folder.glob("**/*"))  # Is a list because it will likely be used more than once.




class FileSort:
	""" Sorts files by their filetype."""
	def run(self, folder:Path, destination:Path):
		pass
	@staticmethod
	def sort_files_by_type(files: List[Path]) -> Dict[str, List[Path]]:
		filetype_index: Dict[str, List[Path]] = dict()

		for filename in files:
			suffix = filename.suffix

			if suffix in filetype_index:
				filetype_index[suffix].append(filename)
			else:
				filetype_index[suffix] = [filename]
		return filetype_index

class ImageSort:
	image_extensions = ['.jpg', '.jpeg', 'png']

	def run(self, source: Path, destination: Path):
		all_files = self.collect_all_files(source)
		all_images = [i for i in all_files if self.is_image(i)]

		for image_filename in all_images:
			resolution = self.get_image_size(image_filename)

			destination_folder = self.get_destination_folder(destination, resolution)
			if not destination_folder.exists():
				destination_folder.mkdir()

			destination_filename = destination_folder / image_filename.name

			image_filename.rename(destination_filename)

	@staticmethod
	def get_destination_folder(destination: Path, resolution: int) -> Path:

		mp = resolution / 1024 ** 2

		intsize = int(mp)
		if intsize == 0:
			floatsize = int(mp * 10) / 10
			folder_name = f"{floatsize}MP"
		else:
			folder_name = f"{intsize}MP"

		return destination / folder_name

	def is_image(self, filename: Path) -> bool:
		return filename.suffix.lower() in self.image_extensions

	@staticmethod
	def get_image_size(filename: Path) -> int:
		image = Image.open(filename)
		height, width = image.size
		resolution = height * width
		return resolution

	@staticmethod
	def collect_all_files(source: Path) -> List[Path]:
		return list(source.glob("**/*"))


def create_parser(args: Optional[List[str]] = None):
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
	if args:
		args = parser.parse_args(args)
	else:
		args = parser.parse_args()

	if args.destination is None: args.destination = args.source

	return args


def main():
	folder = Path("/home/proginoskes/Downloads/4chan soc whores by chansluts.com/_PASSED/FMU/")
	dest = folder.with_name("sorted_folder")
	if not dest.exists():
		dest.mkdir()

	sorter = ImageSort()

	sorter.run(folder, dest)


if __name__ == "__main__":
	main()
