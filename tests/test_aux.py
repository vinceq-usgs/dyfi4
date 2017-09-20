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


def test_ipe():
    from dyfi import ipes

    func=ipes.aww2014wna # Test this ipe

    assert 7.3<func(7,0.1)<7.4
    assert func(3.5,50,fine=False)==2
    assert 6.9<func(7,10,inverse=True)<7

    func=ipes.aww2014ena # Test this ipe

    assert 8.0<func(7,0.1)<8.1
    assert func(3.5,100,fine=False)==2
    assert 6.4<func(7,10,inverse=True)<6.5


