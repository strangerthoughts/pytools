from .. import filetools
import os
from progressbar import ProgressBar

from pprint import pprint
from  functools import partial
pprint = partial(pprint, width = 200)

class CatagorizeDirectory:
	def __init__(self, folder):
		self.directory = folder

class DuplicateFiles:
	def __init__(self, folder, by = 'md5', **kwargs):
		self.duplicates = self.searchForDuplicateFiles(folder, by, **kwargs)

	def totalSize(self):
		total_size = 0
		for filenames in self.duplicates:
			filename = filenames[0]
			file_size = os.path.getsize(filename)
			total_size += file_size

		return total_size / 1024**2


	def searchForDuplicateFiles(self, folder, by = 'md5', **kwargs):
		""" Searches for duplicate files in a folder.
			Parameters
			----------
				folder: string [Path]
					The folder to search through. subfolders will be included.
				by: {'md5', 'name', 'size'}; default 'md5'
					The method to qualify two files as being the same.
			Return
			------
				duplicates: list<list<string>>
					A list of paired filenames representing identical files.
		"""
		print("Searching for duplicate files...")
		ignored_files = ['desktop.ini', 'README.md', '__init__.py']
		ignored_folders = kwargs.get('ignore_folders', []) + ['.git', '.idea', '.vscode', '__pycache__']

		checked_files = dict()
		total_files = 0
		for i in os.walk(folder):
			total_files += len(i[2])
		print("Searching through {} total files".format(total_files))
		pbar = ProgressBar(max_value = total_files)
		for index, directory in enumerate(os.walk(folder)):
			pbar.update(index)
			path, dirnames, filenames = directory
			for basename in filenames:
				abs_path = os.path.join(path, basename)

				if basename in ignored_files or basename.startswith('~'):
					continue

				if by == 'md5':
					try:
						file_key = filetools.generateFileMd5(abs_path)
					except PermissionError:
						continue
				elif by == 'name':
					file_key = os.path.basename(basename)
				elif by == 'size':
					file_key = os.path.getsize(abs_path)
				else:
					raise NotImplementedError

				if file_key in checked_files:
					checked_files[file_key].append(abs_path)
				else:
					checked_files[file_key] = [abs_path]

			_dnames = [i for i in dirnames if i in ignored_folders]


		_duplicates = [v for k, v in checked_files.items() if len(v) > 1]
		print("Finished looking for duplicate files.")
		print("Found {} duplicates.".format(len(_duplicates)))
		return _duplicates

	def removeDuplicates(self, confirm = False, keep = 'first'):
		total_size = 0
		total_files = 0

		for duplicate_files in self.duplicates:
			for i in duplicate_files[1:]:
				total_files += 1
				total_size += os.path.getsize(i)
				if confirm:
					os.remove(i)
		print("Removed {} files totaling {:.2f}MB".format(total_files, total_size / 1024**2))

	def listDuplicates(self):
		for duplicate_files in self.duplicates:
			for filename in duplicate_files:
				print("{:5.2f}MB\t'{}'".format(os.path.getsize(filename)/1024**2, filename))