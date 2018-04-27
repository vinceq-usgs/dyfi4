# To run this test, you must be at the package root directory and run:
# pytest tests/test_run.py

import pytest
import shutil
from argparse import Namespace
import warnings

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_run():
    from app import rundyfi

    if testid:
        shutil.rmtree('data/'+testid,ignore_errors=True)

    with pytest.raises(RuntimeError) as exception:
        rundyfi.main(Namespace(evid='blank',configfile=configfile))
    assert 'Cannot create Event' in str(exception.value)

    container=rundyfi.main(Namespace(evid=testid,configfile=configfile))
    products=container.products
    assert len(products.products)==6
    assert 'Products' in str(products)

    from dyfi import Contents
    contents=Contents(container)
    data=contents.toXML(save=False)
    assert 'dyfi_geo_10km.png' in data

