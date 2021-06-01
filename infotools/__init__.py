from . import *
# TODO: Move the scripts to a separate repo.
from loguru import logger

DEBUG = False

if not DEBUG:
	import sys
	logger.remove()
	logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
