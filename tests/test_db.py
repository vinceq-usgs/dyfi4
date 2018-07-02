# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
from dyfi import Config,Db

testid='ci37511872'
configfile='tests/testconfig.yml'
config=Config(configfile)


def test_db():

  db=Db(config)
  rawdb=db.rawdb

  raw=db.loadEvent(testid)
  assert isinstance(raw['lat'],float)
  assert isinstance(raw['lon'],float)
  assert isinstance(raw['mag'],float)


  import datetime
  year = datetime.datetime.utcnow().year
  assert str(year) in Db.epochToString()

   # Test RawDb

  with pytest.raises(ValueError) as exception:
    rawdb.querySingleTable('badtable','suspect=1')
  assert 'Invalid table' in str(exception.value)

  with pytest.raises(RuntimeError) as exception:
    rawdb.querySingleTable('event','invalid command')
  assert 'Operational error' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    rawdb.getCursor('badtable')
  assert 'getCursor could not find table' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    rawdb.getColumns('badtable')
  assert 'Invalid table' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    rawdb.updateRow('badtable',999,'k','v')
  assert 'Invalid table' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    rawdb.save('badtable',{'k':'v'})
  assert 'Invalid table' in str(exception.value)

  with pytest.raises(ValueError) as exception:
    rawdb.createTable('dbfile',table='badtable')
  assert 'Invalid table' in str(exception.value)


def test_saveEvent():

  from dyfi import Event
  db=Db(config)

  # Test saving dict
  obj={'eventid':'testid','table':'event'}
  db.save(obj)

  # Test missing table
  event=Event(testid,config)
  event.__dict__['table']=None
  with pytest.raises(ValueError) as exception:
    db.save(event)
  assert 'table not specified' in str(exception.value)

  # Test invalid table
  event.__dict__['table']='invalidtable'
  with pytest.raises(RuntimeError) as exception:
    db.save(event)
  assert 'unsupported table' in str(exception.value)

  event.__dict__['table']='event'
  mag=event.mag
  # Make a change and save...
  event.__dict__['mag']=11

  print('Saving id',testid,'mag: 11')
  returnid=db.save(event)
  assert returnid==testid
  event=Event(testid,config)
  assert event.mag==11

  # Now change it back
  event.__dict__['mag']=mag
  assert db.save(event)==returnid
  event=Event(testid,config)
  assert event.mag==mag


def test_saveEntry():

  import datetime

  db=Db(config)
  rawdb=db.rawdb

  testyear=2016
  testtable='extended_'+str(testyear)

  rows=db.loadEntries(
    startdatetime=datetime.datetime(testyear,1,1),
    querytext='eventid="%s"' % testid)
  row=rows[0]
  testsubid=row['subid']
  # Test overwriting this entry

  row['street']='test street'
  subid=db.save(row,table='extended')
  assert subid==testsubid

  row2=rawdb.querySingleTable(testtable,'subid=?',subid)[0]
  assert row2['street']==row['street']

  row['street']='[REDACTED]'
  subid=db.save(row,testtable)
  assert subid==testsubid


def test_saveRawdb():

  db=Db(config)
  rawdb=db.rawdb

  testtable='extended_2015'
  testsubid=3996579

  # Test rawdb.save
  row=db.rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  origcomment=row['comments']

  assert rawdb.save(testtable,row)==testsubid

  del row['comments']
  assert rawdb.save(testtable,row)==testsubid
  testrow=db.rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert testrow['comments']==None

  row['comments']=origcomment
  assert rawdb.save(testtable,row)==testsubid
  testrow=db.rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert testrow['comments']==origcomment


  row['comments']=origcomment
  assert rawdb.save(testtable,row)==testsubid

  with pytest.raises(RuntimeError) as exception:
    row['subid']='invalidstring'
    rawdb.save(testtable,row)
  assert 'Operational error' in str(exception.value)


  # Test updateRow

  assert rawdb.updateRow(testtable,testsubid,'comments','foo')==1
  row=rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert row['comments']=='foo'

  assert rawdb.updateRow(testtable,testsubid,'comments',origcomment)==1
  row=rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert row['comments']==origcomment

  # Test updateRow increment
  testevent=rawdb.querySingleTable('event','eventid=?',testid)[0]
  assert not rawdb.updateRow('event',testid,'newresponses','badvalue',increment=True)

  assert rawdb.updateRow('event',testid,'newresponses',99)
  assert rawdb.updateRow('event',testid,'newresponses',1,increment=True)
  testevent=rawdb.querySingleTable('event','eventid=?',testid)[0]
  assert testevent['newresponses']==100
  rawdb.updateRow('event',testid,'newresponses',0)

  with pytest.raises(RuntimeError) as exception:
    rawdb.updateRow('event',testid,'badcolumn',None)
  assert 'Operational error' in str(exception.value)

  assert rawdb.updateRow('event',testid,'mag',3)==1

