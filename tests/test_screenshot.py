# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
from .context import dyfi

testid='ci37511872'

def test_staticmap():
    import os
    from dyfi import Config,Map

    infile='tests/data/dyfi_geo_10km.geojson'
    blankfile='tests/data/blank.geojson'
    outfile='tests/data/dyfi_geo_10km.png'

    config=Config('tests/testconfig.yml')

    # Test that old PNG file is properly removed
    screenshotfile='leaflet/screenshot.png' 
    with open(screenshotfile,'w') as tmp:
      tmp.write('Test output')

    output=Map.GeoJSONtoImage(blankfile,outfile,config)
    assert output==None
    assert not os.path.isfile(screenshotfile)

    output=Map.GeoJSONtoImage(blankfile,'/bad_directory',config)
    assert output==None
 
    output=Map.GeoJSONtoImage(infile,outfile,config)
    assert output==outfile
    assert os.path.isfile(output)
    assert os.path.getsize(output)>=100000


