from .. import filetools
import os
def searchForDuplicateFiles(folder, by = 'name'):
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
	_ignored_files = [
		'desktop.ini', 'README.md'
	]
	all_files = filetools.listAllFiles(folder)

	checked_files = dict()
	_duplicate_keys = list()
	for filename in all_files:
		basename = os.path.basename(filename)
		if basename in _ignored_files:
			continue
		if basename.startswith('~'): continue
		if by == 'md5':
			file_key = filetools.generateFileMd5(filename)
		elif by == 'name':
			file_key = os.path.basename(filename)
		elif by == 'size':
			file_key = os.path.getsize(filename)

		if file_key in checked_files:
			checked_files[file_key].append(filename)
			_duplicate_keys.append(file_key)
		else:
			checked_files[file_key] = [filename]
	_duplicates = list()
	for key in _duplicate_keys:
		_duplicates.append(checked_files[key])
	_duplicates = {k:v for k,v in checked_files.items() if len(v) > 1}

	return _duplicates