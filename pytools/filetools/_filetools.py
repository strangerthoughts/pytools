
import hashlib

from pathlib import Path
import os
import psutil

def memoryUsage(show = True, units = 'MB'):
	""" Gets the current memory usage
		Returns
		----------
			if show is False
			memory: int
				The total number of bytes being used by the current process
	"""

	process = psutil.Process(os.getpid())
	usage = process.memory_info().rss
	if show:
		if units == 'MB':
			value = usage / 1024**2
		else:
			value = usage
		print("Current memory usage: {0:.2f}{1}".format(value, units), flush = True)
	else:
		return usage

def checkDir(path:Path, full = False):
	""" Creates a folder if it doesn't already exist.
		Parameters
		----------
			path: Path
				Path to a folder.
			full: bool; default False
				If true, will create any parent folders
				if they do not already exists.
		Returns
		-------
			status: bool
				Whether the folder was successfully created.
	"""
	if path.is_dir() and not path.exists():
		path.mkdir()
	return path.exists()



def generateFileMd5(filename:str, blocksize:int=2**20)->str:
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



if __name__ == "__main__":
	pass

