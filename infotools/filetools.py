import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Tuple, Union

mimetypes.add_type('audio/aac', '.aac')

from loguru import logger

Pathlike = Union[str, Path]


def get_mimetype(filename: Pathlike) -> Tuple[str, str]:
	""" Wrapper to get the mimetype of a given file. Returns `None` if the mimetype cannot be determined.
		Returns
		-------
		mimetype, filetype
	"""
	# Cast to Path so that we can use Path methods
	filename = Path(filename)
	# TODO: Include `folder` as a valid mimetype/filetype?
	mtype = mimetypes.guess_type(str(filename))
	mtype, *_ = mtype
	if mtype:
		type_mime = tuple(mtype.split('/')) # Cast to tuple for consistency
	else:
		logger.warning(f"Could not determine the mimetype of {filename}: {mtype}")
		type_mime = 'unknown', filename.suffix
	return type_mime


def memory_usage(show = True, units = 'MB'):
	""" Gets the current memory usage
		Returns
		----------
			if show is False
			memory: int
				The total number of bytes being used by the current process
	"""
	import psutil
	process = psutil.Process(os.getpid())
	usage = process.memory_info().rss
	if show:
		if units == 'MB':
			value = usage / 1024 ** 2
		else:
			value = usage
		print("Current memory usage: {0:.2f}{1}".format(value, units), flush = True)
	else:
		return usage


def checkdir(path: Pathlike) -> Path:
	""" Creates a folder if it doesn't already exist.
		Parameters
		----------
			path: Path
				Path to a folder.
		Returns
		-------
		Path: The path that was checked.
	"""
	path = Path(path)
	# if path.is_dir() and not path.exists():
	if path.is_dir() and not path.exists():
		path.mkdir()
	return path

def copyfile(source:Path, target:Path)->Path:
	target.write_bytes(source.read_bytes())
	return target


def generate_md5(filename: Union[str, Path], blocksize: int = 2 ** 20) -> str:
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
	with open(str(filename), "rb") as f:
		while True:
			buf = f.read(blocksize)
			if not buf: break
			m.update(buf)
	return m.hexdigest()


if __name__ == "__main__":
	pass
