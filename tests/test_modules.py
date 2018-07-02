# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
import shutil
import copy

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_config():
    from dyfi import Config
    import os

    conf=Config(configfile)

    # conf should have at least 'db' and 'mail' fields
    assert len(list(conf))>=2

    # conf should have string representation
    assert str(conf)

    # test databases should exist
    assert conf.db['type']=='sqlite3' or conf.db['type']=='mysql'
    assert os.path.isfile(conf.db['files']['event'])
    assert '__EXTENDED__' in conf.db['files']['extended']

    assert 'mailbin' in conf.mail
    #Not checking if mailbin is a valid command
    #assert(os.path.isfile(conf.mail['mailbin']))


def test_event():
  import geojson
  from dyfi import Config,Db,Event

  config=Config(configfile)
  db=Db(config)
  event=Event(db.loadEvent(testid))
  assert isinstance(event.lat,float)
  assert isinstance(event.lon,float)
  assert isinstance(event.mag,float)

  event=Event(testid,config=config)
  assert 'Event' in str(event)
  assert isinstance(event.lat,float)
  assert isinstance(event.lon,float)
  assert isinstance(event.mag,float)

  geo=event.toGeoJSON()
  assert isinstance(geo,geojson.Feature)
  assert geo.properties['mag']==3.0

  # Test attributes
  attr=event.eventdatetime
  assert isinstance(attr,str)
  assert testid in repr(event)

  with pytest.raises(ValueError) as exception:
    print(event.invalidcolumn)
  assert 'Invalid column' in str(exception.value)

  # Test an event with no db entry
  with pytest.raises(RuntimeError) as exception:
      event=Event('blank',config=config)
  assert 'Cannot create Event' in str(exception.value)

  # Test setattr
  event.setattr('mag',9)
  with pytest.raises(ValueError) as exception:
      event.setattr('badcolumn',1)
  assert 'Invalid column' in str(exception.value)

  # Test a stub event
  event=Event({'eventid':'testStub'},config=config)
  assert event.isStub


def test_entries():
  from dyfi import Config,Event,Entries,Db,aggregate
  import geojson

  testtable='extended_2016'

  shutil.rmtree('data/'+testid,ignore_errors=True)

  config=Config(configfile)
  db=Db(config)

  with pytest.raises(RuntimeError) as exception:
      Entries()
  assert 'No evid or Event object' in str(exception.value)

  # Test loading Entries with raw data

  rawentries=db.loadEntries(testid,table=testtable)
  entries=Entries(testid,rawentries=rawentries)
  assert len(entries)>9

  # Test loading Entries with event
  event=Event(testid,config=config)
  entries=Entries(event=event,config=config)
  count=len(entries)
  assert len(entries)==count
  assert 'Entries[' in repr(entries)
  assert 'Entries' in str(entries)

  # test that entering Entry entries still works
  testentries=Entries(testid,rawentries=entries.entries,config=config)
  assert len(testentries)==count

  # Test row2geojson
  row=rawentries[0]
  feature=db.row2geojson(row)
  assert feature['properties']['street']=='[REDACTED]' or feature['properties']['street']=='test street'
  coords=list(geojson.utils.coords(feature))
  assert coords[0][0]==row['longitude']
  assert isinstance(coords[0][0],float)
  assert coords[0][1]==row['latitude']
  assert isinstance(coords[0][1],float)

  # Test null column value
  row['mag']='null'
  feature=db.row2geojson(row)
  assert feature.properties['mag']==None

  # Tests on a single entry

  assert len(entries)>0
  testentry=entries.entries[0]

  testsubid=testentry.subid
  assert '[Entry: %s:%s' % (testtable,testsubid) in str(testentry)
  assert testsubid!=None
  assert testentry.table==testtable

  # Test aggregate
  assert isinstance(aggregate.aggregate(entries,'geo_1km'),dict)

  with pytest.raises(ValueError) as exception:
      aggregate.aggregate(entries,'geo_11km')
  assert 'unknown type' in str(exception.value)

  single=copy.deepcopy(entries.entries[0])
  assert isinstance(aggregate.getUtmForEntry(single,'1km'),str)

  utmstring='500000 3650000 11 S'

  poly=aggregate.getUtmPolyFromString(utmstring,10000)
  assert aggregate.getUtmFromCoordinates(33,-117,'geo_10km')==utmstring
  poly=aggregate.getUtmPolyFromString(utmstring,10000)
  lonlat=poly['center']['coordinates']
  assert abs(lonlat[1]-33)<0.1
  assert abs(lonlat[0]-(-117))<0.1

  teststring='760000 4250000 17 S'
  poly=aggregate.getUtmPolyFromString(teststring,100000)
  lonlat=poly['center']['coordinates']
  assert abs(lonlat[1]-38.79)<0.1
  assert abs(lonlat[0]-(-77.43))<0.1

  # Test bad span values

  for badvalue in ('geo_9km','9km',9000):
    print('Trying value',badvalue)
    with pytest.raises(TypeError) as exception:
      aggregate.getUtmFromCoordinates(33,-117,badvalue)
    assert 'Invalid span value' in str(exception.value)

  # Test bad lat/lon values

  single.latitude=None
  assert aggregate.getUtmForEntry(single,'1km')==None

  with pytest.raises(ValueError) as exception:
      single.latitude='badvalue'
      aggregate.getUtmForEntry(single,'1km')
  assert 'could not convert string' in str(exception.value)

  # Test confidence
  single=copy.deepcopy(entries.entries[0])
  single.confidence=None
  single.latitude=33.8
  single.longitude=-117.1
  assert not aggregate.checkConfidence(single,'10km')
  single.latitude=34
  assert not aggregate.checkConfidence(single,'10km')

  with pytest.raises(ValueError) as exception:
      db.getExtendedTablesByDatetime(None)
  assert 'Got blank date' in str(exception.value)


def test_container():
  from dyfi import DyfiContainer

  # Note that individual packages will raise their own exceptions
  # no need to test here

  with pytest.raises(RuntimeError) as e:
    DyfiContainer('blank')
  assert 'Cannot create Event' in str(e.value)



