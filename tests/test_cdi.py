# To run this test, you must be at the package root directory and run:
# pytest tests/test_modules.py

import pytest
import shutil

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_cdi():
  from dyfi import cdi,Entry
 
  # Tests of felt and other_felt

  entry=Entry({'felt':1,'other_felt':0})
  assert cdi.getFeltFromOther(entry)==1
  entry=Entry({'felt':0,'other_felt':0})
  assert cdi.getFeltFromOther(entry)==0

  entry=Entry({'felt':1,'other_felt':2})
  assert cdi.getFeltFromOther(entry)==0.36
  entry=Entry({'felt':0,'other_felt':2})
  assert cdi.getFeltFromOther(entry)==0

  entry=Entry({'felt':1,'other_felt':3})
  assert cdi.getFeltFromOther(entry)==0.72
  entry=Entry({'felt':0,'other_felt':3})
  assert cdi.getFeltFromOther(entry)==0.72

  entry=Entry({'felt':0,'other_felt':4})
  assert cdi.getFeltFromOther(entry)==1

  entry=Entry({'felt':0,'other_felt':5})
  assert cdi.getFeltFromOther(entry)==1

  # Tests of d_text

  assert cdi.getDamageFromText('_none')==0
  assert cdi.getDamageFromText('_crackmin')==0.5
  assert cdi.getDamageFromText('_crackwallfew')==0.75
  assert cdi.getDamageFromText('_crackwall')==1
  assert cdi.getDamageFromText('_crackwallfew _crackwall')==1
  assert cdi.getDamageFromText('_crack')==None
  assert cdi.getDamageFromText('_masonryfell')==2
  assert cdi.getDamageFromText('_crackmin _pipe')==2
  assert cdi.getDamageFromText('_crackmin _crackwall _wall _chim')==3


def test_ipe():
    from dyfi import ipes
    mag=6.5
    r=2
    for ipe in ipes.ipelist:
        i=ipe(mag,r)
        print('mag:',mag,'r:',r,'i:',i)
        assert i>2

    r=10000
    for ipe in ipes.ipelist:
        i=ipe(mag,r)
        print('mag:',mag,'r:',r,'i:',i)
        assert i<=1


def test_filter():
    from dyfi import Config,Event,Filter

    config=Config(configfile)
    event=Event(testid,config=config)
    event.mag=2
    f=Filter(event,config)

    func=f.filterFunction();
    goodcoords=[event.lon,event.lat]

    testentry={
        'properties':{ 'intensity':2 }
    }

    with pytest.raises(ValueError) as exception:
        func(testentry)
    assert 'Cannot find coordinates' in str(exception.value)

    testentry['properties']['center']={ 'coordinates':goodcoords }
    print(testentry)
    assert not func(testentry)

    # Test very very far distance
    coords=[event.lon,event.lat-90]
    testentry['properties']['center']['coordinates']=coords
    assert func(testentry)==2

    # Test approx. 200 km away
    coords=[event.lon+15,event.lat]
    testentry['properties']['center']['coordinates']=coords
    assert func(testentry)==1

    # Test intensity too high
    testentry['properties']['center']['coordinates']=goodcoords
    testentry['properties']['intensity']=9
    assert func(testentry)==1


