# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
testid='ci37511872'
configfile='tests/testconfig.yml'

@pytest.mark.slow
def test_dbentries():
  from dyfi import Db,Config,Event

  db=Db(Config(configfile))

  # Test when loading without date, use latest table
  entries=db.loadEntries(evid=testid)
  assert len(entries)==0

  # Test loading specific table
  entries=db.loadEntries(evid=testid,table='extended_2016')
  assert len(entries)>=913
  entries=db.loadEntries(evid=testid,table='2015')
  assert len(entries)==0
  entries=db.loadEntries(evid=testid,table='all')
  assert len(entries)>=913
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


