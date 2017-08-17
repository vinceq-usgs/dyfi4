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
    assert str(conf)

    # test databases should exist
    assert conf.db['type']=='sqlite3' or conf.db['type']=='mysql'
    assert os.path.isfile(conf.db['files']['event'])
    assert os.path.isfile(conf.db['files']['maps'])
    assert '__EXTENDED__' in conf.db['files']['extended']

    assert 'mailbin' in conf.mail
    #Not checking if mailbin is a valid command
    #assert(os.path.isfile(conf.mail['mailbin']))


def test_db():
  from dyfi import Config,Db

  db=Db(Config('tests/testconfig.yml'))
  raw=db.loadEvent(testid)
  assert isinstance(raw['lat'],float)
  assert isinstance(raw['lon'],float)
  assert isinstance(raw['mag'],float)

  pasttime=db.timeago(3)
  assert pasttime.year>1990

def test_event():
  import geojson
  import pytest
  import datetime
  from dyfi import Config,Db,Event

  db=Db(Config('tests/testconfig.yml'))
  event=Event(db.loadEvent(testid))
  assert isinstance(event.lat,float)
  assert isinstance(event.lon,float)
  assert isinstance(event.mag,float)

  geo=event.toGeoJSON()
  assert isinstance(geo,geojson.Feature)
  assert geo.properties['mag']==3.0

  # Test attributes
  attr=event.process_timestamp
  assert isinstance(attr,str)
  assert testid in repr(event)

  with pytest.raises(NameError) as badAttr:
    print(event.invalidcolumn)
  assert 'bad column' in str(badAttr.value) 

  # Test an event with no db entry
  with pytest.raises(NameError) as exception:
    event=Event(db.loadEvent('blank'))
  assert str(exception.value)=='Event: Cannot create evid with no data'

    
def test_entries():
  import geojson
  import datetime
  from dyfi import Config,Db,Event

  db=Db(Config('tests/testconfig.yml'))
  entries=db.loadEntries(testid)
  assert len(entries)>9

  entries=db.loadEntries(evid=testid,table='latest')
  assert len(entries)>0
  entries=db.loadEntries(evid=testid,table='2015')
  assert len(entries)==0
  entries=db.loadEntries(evid=testid,table='all')
  assert len(entries)>0
  with pytest.raises(NameError) as testBadTable:
    entries=db.loadEntries(evid=testid,table='2099')
  assert 'getcursor could not find table' in str(testBadTable.value)

  with pytest.raises(NameError) as testBadTable:
    entries=db.loadEntries(evid=testid,table='1999,2000')
  assert 'Cannot handle string' in str(testBadTable.value)

  with pytest.raises(RuntimeError) as testBadTable:
    db.rawStatement('select * from event where eventid="%s"' % testid)
  assert 'unsafe' in str(testBadTable.value)

  # Test loading entries by event object
  event=Event(db.loadEvent(testid))
  entries=db.loadEntries(event=event)
  assert len(entries)>0

  # Test loading entries by date and query
  entries=db.loadEntries(
    startdatetime='2016-01-01',
    querytext='eventid="%s"' % testid)
  assert len(entries)>0

  entries=db.loadEntries(startdatetime=1990,
    querytext='eventid="%s"' % testid)
  assert len(entries)>0

  entries=db.loadEntries(startdatetime=datetime.datetime(2016,1,1),
    querytext='eventid="%s"' % testid)
  assert len(entries)>0

  with pytest.raises(NameError) as testBadTable:
    db.loadEntries(startdatetime='Stardate 1312.4')
  assert 'Bad year' in str(testBadTable.value)

  testentry=entries[0]
  testentry['orig_id']=''
  feature=db.row2geojson(testentry)
  coords=list(geojson.utils.coords(feature))
  assert len(coords)==1 
  assert isinstance(coords[0][0],float)
  assert isinstance(coords[0][1],float)

  testentry['lat']=None
  feature=db.row2geojson(testentry)
 
 
def test_map():
    from dyfi import Config,Db,Maps

    db=Db(Config('tests/testconfig.yml'))
    maps=Maps(db.loadMaps(testid))
    assert len(maps.maplist)>0
    
    for mapid,thismap in maps.maplist.items():
        assert thismap.eventid==testid
        assert 'Map' in str(thismap)
    
    # Test an event with no maps entry
    maps=Maps(db.loadMaps('blank'))
    assert maps.maplist=={}


def test_container():
  from dyfi import DyfiContainer

  # Note that individual packages will raise their own exceptions
  # no need to test here

  #with pytest.raises(NameError) as badAttr:
  #  container=DyfiContainer('blank')
  #assert 'Cannot create evid' in str(badAttr.value) 
  


