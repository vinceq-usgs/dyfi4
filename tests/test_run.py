# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
import sys
from .context import bin

testid='us10006u0q'

def test_run():
  from argparse import Namespace
  from bin import rundyfi

  rundyfi.main(Namespace(evid=testid,configfile='./tests/testconfig.yml'))

