# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
import shutil

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


def test_db():
  from dyfi import Config,Db,Event

  config=Config(configfile)
  db=Db(config)
  rawdb=db.rawdb

  raw=db.loadEvent(testid)
  assert isinstance(raw['lat'],float)
  assert isinstance(raw['lon'],float)
  assert isinstance(raw['mag'],float)

 # These functions are unused right now but maybe useful later

  assert Db.timeago(60).year>2016
  assert '2018' in Db.epochToString(1515565764)

  import datetime
  year = datetime.datetime.utcnow().year
  assert str(year) in Db.epochToString()

  # Test save function
  assert rawdb.updateRow('event',testid,'mag',3)==1
  event=Event(testid,config)
  mag=event.mag
  print('Saving id',testid,'mag:',mag)

  # Make a change and save...
  event.__dict__['mag']=11
  assert 1==db.save(event)
  event=Event(testid,config)
  assert event.mag==11

  # Now change it back
  event.__dict__['mag']=mag
  assert 1==db.save(event)
  event=Event(testid,config)
  assert event.mag==mag

  # Test missing table
  event.__dict__['table']=None
  with pytest.raises(ValueError) as exception:
    db.save(event)
  assert 'table not specified' in str(exception.value)

  # Test invalid table
  event.__dict__['table']='invalidtable'
  with pytest.raises(RuntimeError) as exception:
    db.save(event)
  assert 'unsupported table' in str(exception.value)

  # Test RawDb

  with pytest.raises(NameError) as exception:
    rawdb.querySingleTable('badtable','suspect=1')
  assert 'getCursor could not find table' in str(exception.value)

  with pytest.raises(RuntimeError) as exception:
    rawdb.querySingleTable('event','invalid command')
  assert 'Operational error' in str(exception.value)

  testtable='extended_2015'
  subid=3996579

  assert rawdb.updateRow(testtable,subid,'comments','foo')==1
  row=rawdb.querySingleTable(testtable,'subid=?',subid)
  assert row[0]['comments']=='foo'

  assert rawdb.updateRow(testtable,subid,'comments','bar')==1
  row=rawdb.querySingleTable(testtable,'subid=?',subid)
  assert row[0]['comments']=='bar'

  # Test rawdb.save
  with pytest.raises(RuntimeError) as exception:
    testentry=row[0]
    testentry['subid']='invalidstring'
    rawdb.save('extended_2015',testentry)
  assert 'Operational error' in str(exception.value)

  # Test updateRow increment
  testevent=rawdb.querySingleTable('event','eventid=?',testid)[0]
  assert rawdb.updateRow('event',testid,'newresponses',99)
  assert rawdb.updateRow('event',testid,'newresponses',1,increment=True)
  testevent=rawdb.querySingleTable('event','eventid=?',testid)[0]
  assert testevent['newresponses']==100
  rawdb.updateRow('event',testid,'newresponses',0)

  with pytest.raises(RuntimeError) as exception:
    rawdb.updateRow('event',testid,'badcolumn',None)
  assert 'Operational error' in str(exception.value)


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


def test_dbentries():
  import geojson
  import datetime
  from dyfi import Db,Config,Event

  db=Db(Config(configfile))
  entries=db.loadEntries(evid=testid,table='extended_2016')
  assert len(entries)==913

  entries=db.loadEntries(evid=testid,table='2015')
  assert len(entries)==0
  entries=db.loadEntries(evid=testid,table='all')
  assert len(entries)==913
  entries=db.loadEntries(evid=testid,table='latest')
  assert len(entries)==0

  with pytest.raises(ValueError) as exception:
    entries=db.loadEntries(evid=testid,table='2099')
  assert 'no such table' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    entries=db.loadEntries(evid=testid,table='1999,2000')
  assert 'no such table' in str(exception.value)

  querytext='suspect is null or suspect=0'
  entries1=db.loadEntries(table='2015',querytext=querytext)
  entries2=db.loadEntries(table='2016',querytext=querytext)
  entries3=db.loadEntries(table='2015,2016',querytext=querytext)
  entries4=db.loadEntries(table=[2015,2016],querytext=querytext)
  e1=len(entries1)
  e2=len(entries2)
  assert e1>=2017 # This might change from testing
  assert e2>=7
  assert len(entries3)==len(entries4)
  assert e1+e2==len(entries3)

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

  with pytest.raises(ValueError) as exception:
    db.loadEntries(startdatetime='Stardate 1312.4')
  assert 'Bad year' in str(exception.value)

  # Test row2geojson
  testentry=entries[0]
  feature=db.row2geojson(testentry)
  assert feature['properties']['street']=='[REDACTED]' or feature['properties']['street']=='test street'
  coords=list(geojson.utils.coords(feature))
  assert coords[0][0]==testentry['longitude']
  assert isinstance(coords[0][0],float)
  assert coords[0][1]==testentry['latitude']
  assert isinstance(coords[0][1],float)

  # Test null column value
  testentry['mag']='null'
  feature=db.row2geojson(testentry)
  assert feature.properties['mag']==None

  # Test of saving an entry
  testsubid=testentry['subid']
  assert testsubid!=None
  testtable=testentry['table']
  assert testtable!='extended'

  # Test entry save
  testentry['street']='test street'
  assert db.save(testentry,table='extended')==1

  row=db.rawdb.querySingleTable(testtable,'subid=?',testsubid)
  testentry=row[0]
  assert testentry['street']=='test street'

  testentry['street']='[REDACTED]'
  assert db.save(testentry,testtable)==1


def test_entries():
  from dyfi import Config,Event,Entries,Db,aggregate

  shutil.rmtree('data/'+testid,ignore_errors=True)

  config=Config(configfile)

  with pytest.raises(RuntimeError) as exception:
      Entries()
  assert 'No evid or Event object' in str(exception.value)

  # Test loading Entries with raw data

  rawentries=Db(config).loadEntries(testid,table='extended_2016')
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

  # test single entry
  badentry={'subid':1,'table':'extended_pre','badcolumn':0}
  badentries=Entries(testid,rawentries=[badentry],config=config)
  assert len(badentries)==1

  # Test aggregate

  assert isinstance(aggregate.aggregate(entries,'geo_1km'),dict)

  with pytest.raises(ValueError) as exception:
      aggregate.aggregate(entries,'geo_11km')
  assert 'unknown type' in str(exception.value)

  single=entries.entries[0]
  assert isinstance(aggregate.getUtmForEntry(single,'1km'),str)

  utmstring='500000 3650000 11 S'

  poly=aggregate.getUtmPolyFromString(utmstring,10000)
  assert aggregate.getUtmFromCoordinates(33,-117,'geo_10km')==utmstring
  poly=aggregate.getUtmPolyFromString(utmstring,10000)
  lonlat=poly['center']['coordinates']
  assert abs(lonlat[1]-33)<0.1
  assert abs(lonlat[0]-(-117))<0.1

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


def test_products():
    import copy
    from dyfi import Config,Event,Entries,Products,Product,Map,Graph

    shutil.rmtree('data/'+testid,ignore_errors=True)

    config=Config(configfile)
    event=Event(testid,config=config)
    entries=Entries(testid,config=config)

    products=Products(event,entries,config)
    assert str(products)=='Products:[]'

    # Test product with no format
    assert Product(products,name='test',dataset='time')

    with pytest.raises(RuntimeError) as exception:
        Product(products,name='blank',dataset='bad')
    assert 'Unknown datatype' in str(exception.value)

    with pytest.raises(RuntimeError) as exception:
        Product(products,name='test',productFormat='bad')
    assert 'Cannot save' in str(exception.value)

    # Test Map blank directory, GeoJSON output
    products.dir=None
    product=Product(products,name='testmap',dataset='geo_10km',productType='map')
    product.create('geojson','tests/testProduct.geojson')
    myMap=product.data
    assert type(myMap).__name__=='Map'

    # Test Map without directory
    data=myMap.data
    myMap=Map('test_geo_10km',event,data,config)
    assert myMap.toGeoJSON(filename='tests/testMap.geojson')

    badconfig=copy.deepcopy(config)
    badconfig.executables['screenshot']='badexec'
    with pytest.raises(RuntimeError) as exception:
        Map.GeoJSONtoImage('tests/testMap.geojson','tests/testMap.png',badconfig)
    assert 'subprocess call' in str(exception.value)

    # Test blank product
    assert products.create({})==0

    # Test graph functions

    with pytest.raises(RuntimeError) as exception:
        graph=Graph('badtype',event=event,data=None,config=config)
    assert 'Graph got unknown graph type' in str(exception.value)

    # Test when redoing graph data
    data=entries.aggregate('geo_10km')
    graph=Graph('plot_atten',event=event,data=data,config=config,eventDir='test')
    graph.getScatterData()
    graph.getDistBins()
    assert 'data' in graph.toJSON()

    # Test time graph

    data=entries.getTimes('plot_numresp')
    graph=Graph('plot_numresp',event=event,data=data,config=config,eventDir='test')

    # Test no time data

    data['data']=[]
    graph=Graph('plot_numresp',event=event,data=data,config=config,eventDir='test')
    assert graph.data['preferred_unit']=='minutes'


def test_container():
  from dyfi import DyfiContainer

  # Note that individual packages will raise their own exceptions
  # no need to test here

  with pytest.raises(RuntimeError) as e:
    DyfiContainer('blank')
  assert 'Cannot create Event' in str(e.value)

