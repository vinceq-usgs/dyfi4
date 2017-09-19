# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
import sys
import os

from .context import bin

testid='us10006u0q'

def test_run():
    from argparse import Namespace
    from bin import rundyfi

    os.makedirs('data/'+testid,exist_ok=True)

    with pytest.raises(NameError) as testBadTable:
        rundyfi.main(Namespace(evid='blank',configfile='./tests/testconfig.yml'))

    container=rundyfi.main(Namespace(evid=testid,configfile='./tests/testconfig.yml'))

