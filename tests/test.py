# To run this test, you must be at the package root directory and run:
# pytest tests/test.py

import pytest
from .context import dyfi

testid='ci37511872'

def test_config():
    from dyfi import Config
    import os

    conf=Config('tests/testconfig.yml')

    # conf should have at least 'db' and 'mail' fields
    assert len(list(conf))>=2

    # conf should have string representation
    assert(str(conf))

    # test databases should exist
    assert(conf.db['type']=='sqlite3' or conf.db['type']=='mysql')
    assert(os.path.isfile(conf.db['files']['event']))
    assert(os.path.isfile(conf.db['files']['maps']))
    assert('__EXTENDED__' in conf.db['files']['extended'])

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

    entries=db.loadEntries('ci37511872')
    assert(len(entries)>9)

    entries=db.loadEntries(evid='ci37511872',table='latest')
    assert(len(entries)>0)
    entries=db.loadEntries(evid='ci37511872',table='2015')
    assert(len(entries)==0)
    entries=db.loadEntries(evid='ci37511872',table='all')
    assert(len(entries)>0)
    with pytest.raises(NameError) as testBadTable:
      entries=db.loadEntries(evid='ci37511872',table='2099')
    assert 'getcursor could not find table' in str(testBadTable.value)

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
