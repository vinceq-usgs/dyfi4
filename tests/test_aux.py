# Tests of obsolete or not-yet-used functionality
# To run this test, you must be at the package root directory and run:
# pytest tests/test_aux.py

import pytest
from .context import dyfi

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_aggregate():
    from dyfi import aggregate

    aggregate.myCeil(17,10)==20

