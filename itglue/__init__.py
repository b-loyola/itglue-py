"""A simple wrapper for the IT Glue API"""

from .connection import connection
from .path_processor import process_path, PathProcessor
from .resources import *

__version__ = '0.2.0'
