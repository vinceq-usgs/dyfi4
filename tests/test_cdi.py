import pytest

rawentry={
    'felt':'1 yes',
    'other_felt':'0.36 some',
    'stand':'2',
    'shelf':'3', 
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
    assert testentry.cdiIndex('picture')==None

    with pytest.raises(AttributeError) as exception:
        testentry.cdiIndex('badindex')
    assert 'Invalid Entry index' in str(exception.value)



def test_ipes():
    from dyfi import ipes,Entry
 
    testentry=Entry(rawentry)
    val=ipes.aw2007ceus(7,20)
    assert abs(val-8.759)<0.001

    val=ipes.aw2007ceus(3,400,fine=True)
    assert abs(val-1.592)<0.001

    assert ipes.aw2007ceus(3,400)==2
    assert ipes.aw2007ceus(3,1000)==1

    # aw2007ceus cannot do inverse
    assert ipes.aw2007ceus(5,50,inverse=True)==None

    assert ipes.aww2014wna(3,100)==1

