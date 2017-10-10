
import hashlib
import os



def checkDir(path, full = False):
	""" Creates a folder if it doesn't already exist.
		Parameters
		----------
			path: string
				Path to a folder.
			full: bool; default False
				If true, will create any parent folders
				if they do not already exists.
		Returns
		-------
			status: bool
				Whether the folder was successfully created.
	"""
	try:
		if not os.path.exists(path):
			if full:
				os.makedirs(path)
			else:
				os.mkdir(path)
	except FileNotFoundError:
		_concat_path = os.path.dirname(path)
		while not os.path.exists(_concat_path):
			_concat_path = os.path.dirname(_concat_path)
		message = "The path doesn't exist: {} ({})".format(path, _concat_path)
		raise FileNotFoundError(message)

	return os.path.exists(path)



def generateFileMd5(filename, blocksize=2**20):
	""" Generates the md5sum of a file. Does
		not require a lot of memory.
		Parameters
		----------
			filename: string
				The file to generate the md5sum for.
			blocksize: int; default 2**20
				The amount of memory to use when
				generating the md5sum string.
		Returns
		-------
			md5sum: string
				The md5sum string.
	"""
	m = hashlib.md5()
	with open(filename, "rb") as f:
		while True:
			buf = f.read(blocksize)
			if not buf: break
			m.update(buf)
	return m.hexdigest()


def listAllFiles(folder, **kwargs):
	""" Lists all files in a folder. Includes subfolders.
		Parameters
		----------
			folder: string
				The folder to search through.
		Keyword Arguments
		-----------------
			exclude: string, list<string>; default []
				A path or list of paths to exclude from the recursive search.
			logic: {'or', 'and'}; default 'or'
				The logic to use when applying the exclusion criteria.
		Returns
		-------
			list<string>
				A list of all files that were found.
	"""
	exclude = kwargs.get('exclude', [])
	if isinstance(exclude, str): exclude = [exclude]
	logic = kwargs.get('logic', 'or')
	
	file_list = list()
	if os.path.isdir(folder):

		for subfn in os.listdir(folder):
			abs_path = os.path.join(folder, subfn)
			if logic == 'or':
				skip_file = any(e in abs_path for e in exclude)
			elif logic == 'and':
				skip_file = all(e in abs_path for e in exclude)
			else:
				skip_file = False

			if skip_file: continue
			if os.path.isdir(abs_path):
				try:
					file_list += listAllFiles(abs_path, **kwargs)
				except PermissionError:
					pass
					#print(abs_path)
			elif os.path.isfile(abs_path):  # Explicit check
				file_list.append(abs_path)

	else:
		file_list = [folder]
	return file_list


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
	all_files = listAllFiles(folder)

	checked_files = dict()
	_duplicate_keys = list()
	for filename in all_files:
		if by == 'md5':
			file_key = generateFileMd5(filename)
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
	return _duplicates

def searchFiles(string, folder):
	found = []
	all_files = listAllFiles(folder)
	for subfn in all_files:
		if string in subfn:
			found.append(subfn)

	return found


if __name__ == "__main__":
	test_folder = "C:\\Program Files (x86)"
	search_result = searchFiles('basetsd.h', test_folder)

	for fn in search_result:
		print(fn)

