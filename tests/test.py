# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

from .context import dyfi

testid='ci37511872'

def test_config():
    from dyfi import Config
    import os

    conf=Config('tests/testconfig.yml')

    # conf should have at least 'db' and 'mail' fields
    allkeys=list(conf)
    assert(len(allkeys)>=2)
    assert(str(conf))
    assert('mailbin' in conf.mail)
    #Not checking if mailbin is a valid command
    #assert(os.path.isfile(conf.mail['mailbin']))


def test_db():
    from dyfi import Config,Db

    db=Db(Config('tests/testconfig.yml'))
    data=db.loadEvent('ci37511872')
    assert(isinstance(data['lat'],float))
    assert(isinstance(data['lon'],float))
    assert(isinstance(data['mag'],float))

def test_event():
    from dyfi import Config,Db,Event
    import geojson
    import pytest

    db=Db(Config('tests/testconfig.yml'))
    event=Event(db.loadEvent(testid))
    geo=event.toGeoJSON()
    assert(isinstance(geo,geojson.Feature))
    assert(geo.properties['mag']==3.0)

    # Now test an event with no db entry
    with pytest.raises(NameError) as exception:
        event=Event(db.loadEvent('blank'))

    assert(str(exception.value)=='Event: Cannot create Event with no data')

    
def test_map():
    from dyfi import Config,Db,Maps

    db=Db(Config('tests/testconfig.yml'))
    maps=Maps(db.loadMaps(testid))
    print(maps)
    assert(len(maps.maplist)>0)
    
    for mapid,thismap in maps.maplist.items():
        print(thismap)
        assert(thismap.eventid==testid)
    
    # Now test an event with no maps entry
    maps=Maps(db.loadMaps('blank'))
    assert(maps.maplist=={})
