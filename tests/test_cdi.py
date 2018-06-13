import pytest

testid='ci37511872'
configfile='tests/testconfig.yml'

rawentry={
    'felt':'1 yes',
    'other_felt':'0.36 some',
    'stand':'2',
    'shelf':'3',
    'picture':'',
    'd_text':'_chim'
}


def test_cdi():
    from dyfi import cdi,Entry

    testentry=Entry(rawentry)
    assert cdi.calculate(testentry)==8.1
    assert cdi.calculate(testentry,cwsOnly=True)==39.0
    assert cdi.getDamageFromText('_crackwallfew')==0.75

    assert testentry.cdiIndex('shelf')==3
    assert testentry.cdiIndex('other_felt')==0.36
    assert testentry.cdiIndex('d_text')==rawentry['d_text']
    assert testentry.cdiIndex('motion')==None
    assert testentry.cdiIndex('picture')==None

    with pytest.raises(AttributeError) as exception:
        testentry.cdiIndex('badindex')
    assert 'Invalid Entry index' in str(exception.value)


def test_filter():
  from dyfi import Config,Event,Filter

  config=Config(configfile)
  event=Event(testid,config=config)
  filter=Filter(event,config=config,ipe='aww2014ena')

  func=filter.filterFunction()
  testentry=rawentry.copy()

  with pytest.raises(ValueError) as exception:
      func(testentry)
  assert 'Cannot find coordinates' in str(exception.value)

  config.__setattr__('nresp_do_not_filter',None)
  p={
      'center':{
          'coordinates':(event.lon,event.lat),
          'type':'Point'
      },
      'intensityFine':9,
      'nresp':1
  }
  testentry['properties']=p

  # Test nresponse no-filter setting
  p['nresp']=99
  assert func(testentry)==0
  p['nresp']=1
  assert func(testentry)==1

  # Test if greater than max possible distance
  p['center']['coordinates']=(0,0)
  assert func(testentry)==2

  # Test IPE high threshold setting
  p['center']['coordinates']=(event.lon,event.lat)
  testentry['stand']='9'
  testentry['shelf']='9'
  testentry['picture']='9'
  testentry['d_text']='_move'
  assert func(testentry)==1

  # Test IPE low threshold setting
  p['center']['coordinates']=(event.lon+20,event.lat)
  assert func(testentry)==1


def test_ipes():
    from dyfi import ipes

    #testentry=Entry(rawentry)
    val=ipes.aw2007ceus(7,20)
    assert abs(val-8.759)<0.001

    val=ipes.aw2007ceus(3,400,fine=True)
    assert abs(val-1.592)<0.001

    assert ipes.aw2007ceus(3,400)==2
    assert ipes.aw2007ceus(3,1000)==1

    # aw2007ceus cannot do inverse
    assert ipes.aw2007ceus(5,50,inverse=True)==None

    assert ipes.aww2014wna(3,100)==1

