# To run this test, you must be at the package root directory and run:
# pytest tests/test_run.py

import pytest
import os
from argparse import Namespace

testid='us10006u0q'

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

