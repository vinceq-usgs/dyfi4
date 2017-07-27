# Copied from Hitchhiker's Guide to Python. This adds the dyfi package
# to all tests.
#
# Now, to import dyfi in all tests, use this in every test module:
# from .context import dyfi

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dyfi
import bin
