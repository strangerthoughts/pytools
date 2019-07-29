from pathlib import Path


class FolderCount:
	def __init__(self, levels:int = 0):
		""" It will be more convienient to store the maximum level as a class property rather than a global variable."""
		self.levels = levels # THe maximum number of subfolders to move into.
		self.records= list()

	def run(self, folder:Path):

		self.count(folder)

		self.show()

	def count(self, parent: Path, level = 0)->int:
		""" Prints the number of files in a folder."""
		file_count = 0
		if parent.is_file() or level > self.levels:
			return file_count

		if level:
			indent = '\t' * level
		else:
			indent = ''

		for item in parent.iterdir():
			if item.is_dir():
				self.count(item, level+1)
			else:
				file_count += 1

		record = {
			'path': parent.absolute(),
			'files': file_count,
			'level': level
		}
		self.records.append(record)
		return file_count
	def show(self):
		for record in sorted(self.records, key = lambda s: (s['level'], s['files'])):
			files = record['files']
			name = record['path'].name
			line = self._get_indent(record['level']) + f"{files}\t{name}"
			print(line)

	def _get_indent(self, level)->str:
		if level:
			indent = '\t' * level
		else:
			indent = ''
		return indent

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"path",
		help = "The folder to count files in.",
		type = Path
	)
	parser.add_argument(
		"-l", "--level",
		help = "The number of subdirectories to move into.",
		type = int,
		default = 0
	)
	args =  parser.parse_args(["-l", "2", "/home/proginoskes/Documents/GitHub/infotools/infotools/"])
	counter = FolderCount(levels = args.level)
	counter.run(args.path)