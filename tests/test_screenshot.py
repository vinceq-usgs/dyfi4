# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
from .context import dyfi

testid='ci37511872'

def test_staticmap():
    import os
    from dyfi import Config,staticMap

    infile='tests/data/dyfi_geo_10km.geojson'
    outfile='tests/data/dyfi_geo_10km.png'

    config=Config('tests/testconfig.yml')
    output=staticMap.createFromGeoJSON(infile,outfile,config,verbose=True)
    assert(output)
    assert(os.path.isfile(output))
    assert(os.path.getsize(output)>=100000)


