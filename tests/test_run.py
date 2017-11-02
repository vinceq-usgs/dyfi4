# To run this test, you must be at the package root directory and run:
# pytest tests/test_run.py

import pytest
import os
from argparse import Namespace

testid='us10006u0q'


def test_aggregate():
    from dyfi import aggregate

    utmstring='500000 3650000 11 S'
    assert aggregate.main(['33','-117','geo_10km'])==utmstring
    latlon=aggregate.main([utmstring])
    assert abs(latlon[0]-33)<0.1
    assert abs(latlon[1]-(-117))<0.1

    with pytest.raises(ValueError) as exception:
        aggregate.main(['91','-117','geo_1km'])
    assert 'Latitude out of bounds' in str(exception.value)

    try:
        aggregate.main(['bad','worse','geo_1km'])
        assert False
    except SystemExit:
        pass


def test_run():
    from app import rundyfi

    os.makedirs('data/'+testid,exist_ok=True)

    with pytest.raises(NameError) as exception:
        rundyfi.main(Namespace(evid='blank',configfile='./tests/testconfig.yml'))
    assert 'Cannot create evid' in str(exception.value)

    container=rundyfi.main(Namespace(evid=testid,configfile='./tests/testconfig.yml'))

    products=container.products
    assert len(products.products)==6
    assert 'Products' in str(products)

    from dyfi import Contents
    contents=Contents(container)
    data=contents.toXML(save=False)
    assert 'dyfi_geo_10km.png' in data

