from infotools import filetools
import pytest
from pathlib import Path
from loguru import logger
@pytest.mark.parametrize(
	"filename, expected",
	[
		("file1.mp4", ('video', 'mp4')),
		("abc.aac", ("audio", "aac"))
	]
)
def test_get_mimetype(filename, expected):
	assert filetools.get_mimetype(filename) == expected

def test_checkdir(tmp_path):
	folder = Path(__file__).parent / "new"
	result = filetools.checkdir(folder)

	logger.debug(f"Folder: {folder}, {type(folder)}, {folder.exists()}")
	logger.debug(f"result: {result}, {type(result)}, {result.exists()}")
	logger.debug(f"{result == folder}")
	assert result == folder
	assert result.exists()