#! /usr/bin/env python3

import pytest
import os.path
import geojson

from dyfi.modules import Config,Db,Event,Maps,Entries

testid='ci37511872'

def test_config():
    conf=Config('./testconfig.yml')
    assert('mailbin' in conf.mail)
    assert(os.path.isfile(conf.mail['mailbin']))


def test_db():
    db=Db(Config('./testconfig.yml'))
    data=db.loadEvent('ci37511872')
    assert(isinstance(data['lat'],float))
    assert(isinstance(data['lon'],float))
    assert(isinstance(data['mag'],float))

def test_event():
    db=Db(Config('./testconfig.yml'))
    event=Event(db.loadEvent(testid))
    geo=event.toGeoJSON()
    assert(isinstance(geo,geojson.Feature))
    assert(geo.properties['mag']==3.0)

    # Now test an event with no db entry
    with pytest.raises(NameError) as exception:
        event=Event(db.loadEvent('blank'))

    assert(str(exception.value)=='Event: Cannot create Event with no data')

    
def test_map():
    db=Db(Config('./testconfig.yml'))
    maps=Maps(db.loadMaps(testid))
    print(maps)
    assert(len(maps.maplist)>0)
    
    for mapid,thismap in maps.maplist.items():
        print(thismap)
        assert(thismap.eventid==testid)
    
    # Now test an event with no maps entry
    maps=Maps(db.loadMaps('blank'))
    assert(maps.maplist=={})
