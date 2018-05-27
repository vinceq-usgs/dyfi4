# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
import shutil
from dyfi import Config,Db

testid='ci37511872'
configfile='tests/testconfig.yml'
config=Config(configfile)

@pytest.mark.slow
def test_dbentries():
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

  with pytest.raises(ValueError) as exception:
    db.loadEntries(startdatetime='Stardate 1312.4')
  assert 'Bad year' in str(exception.value)


def test_db():

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
  rawdb=db.rawdb

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

  entries=db.loadEntries(
    startdatetime=datetime.datetime(testyear,1,1),
    querytext='eventid="%s"' % testid)
  testentry=entries[0]
  testsubid=testentry['subid']
  # Test overwriting this entry

  testentry['street']='test street'
  subid=db.save(testentry,table='extended')
  assert subid==testsubid

  testentry2=rawdb.querySingleTable(testtable,'subid=?',subid)[0]
  assert testentry2['street']==testentry['street']

  testentry2['street']='[REDACTED]'
  subid=db.save(testentry,testtable)
  assert subid==testsubid


def test_saveRawdb():

  db=Db(config)
  rawdb=db.rawdb

  testtable='extended_2015'
  testsubid=3996579

  # Test rawdb.save
  testentry=db.rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  origcomment=testentry['comments']

  with pytest.raises(RuntimeError) as exception:
    testentry['subid']='invalidstring'
    rawdb.save(testtable,testentry)
  assert 'Operational error' in str(exception.value)

  assert rawdb.updateRow(testtable,testsubid,'comments','foo')==1
  testentry=rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert testentry['comments']=='foo'

  assert rawdb.updateRow(testtable,testsubid,'comments',origcomment)==1
  testentry=rawdb.querySingleTable(testtable,'subid=?',testsubid)[0]
  assert testentry['comments']==origcomment

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

  assert rawdb.updateRow('event',testid,'mag',3)==1
 
