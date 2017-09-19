# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
import sys
import os
from argparse import Namespace

from .context import bin

testid='us10006u0q'


def test_aggregate():
    from dyfi import aggregate

    utmstring='500000 3650000 11 S'
    assert aggregate.main(Namespace(lat=33,lon=-117,span='geo_10km'))==utmstring
    latlon=aggregate.main(Namespace(lat=utmstring))
    assert abs(latlon[0]-33)<0.1
    assert abs(latlon[1]-(-117))<0.1

    with pytest.raises(ValueError) as exception:
        aggregate.main(Namespace(lat=91,lon=-117,span='geo_1km'))
    assert 'Latitude out of bounds' in str(exception.value)

    with pytest.raises(TypeError) as exception:
        aggregate.main(Namespace(lat=None,lon=None,span='geo_1km'))
    assert 'must be a string or a number' in str(exception.value)


def test_run():
    from bin import rundyfi

    os.makedirs('data/'+testid,exist_ok=True)

    with pytest.raises(NameError) as exception:
        rundyfi.main(Namespace(evid='blank',configfile='./tests/testconfig.yml'))

    container=rundyfi.main(Namespace(evid=testid,configfile='./tests/testconfig.yml'))

    products=container.products
    assert len(products.products)==7
    assert 'Products' in str(products)

