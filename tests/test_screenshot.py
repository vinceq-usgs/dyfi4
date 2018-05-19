# To run this test, you must be at the package root directory and run:
# pytest tests/test_screenshot.py

testid='ci37511872'

def test_staticmap():
    import os
    from dyfi import Config,Map

    infile='tests/data/dyfi_geo_10km.geojson'
    blankfile='tests/data/blank.geojson'
    outfile='tests/data/dyfi_geo_10km.png'

    config=Config('tests/testconfig.yml')

    output=Map.GeoJSONtoImage(blankfile,'/bad_directory',config)
    assert output==None

    output=Map.GeoJSONtoImage(infile,outfile,config)
    assert output==outfile
    assert os.path.isfile(output)
    assert os.path.getsize(output)>=100000


