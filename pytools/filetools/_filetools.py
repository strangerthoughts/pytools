
import hashlib
import os
from typing import List
from pathlib import Path


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

