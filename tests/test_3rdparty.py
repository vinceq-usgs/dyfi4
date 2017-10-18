# To run this test, you must be at the package root directory and run:
# pytest tests/test_3rdparty.py

import pytest
testid='ci37511872'
configfile='tests/testconfig.yml'

def test_gmtcolormap():
    pass


def test_utm():
    from dyfi import utm
    from dyfi.thirdparty.utm import OutOfRangeError

    # to_latlon tests

    with pytest.raises(ValueError) as exception:
        coords=utm.to_latlon(0,0,1)
    assert str(exception.value)=='either zone_letter or northern needs to be set'
    with pytest.raises(ValueError) as exception:
        coords=utm.to_latlon(0,0,zone_number=1,zone_letter='A',northern=True)
    assert str(exception.value)=='set either zone_letter or northern, but not both'
    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.to_latlon(0,999999,1,northern=True)
    assert 'easting out of range' in str(exception.value)

    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.to_latlon(100000,10000001,1,northern=True)
    assert 'northing out of range' in str(exception.value)

    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.to_latlon(100000,0,61,northern=True)
    assert 'zone number out of range' in str(exception.value)

    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.to_latlon(100000,0,1,zone_letter='Y')
    assert 'zone letter out of range' in str(exception.value)

    coords=utm.to_latlon(100000,0,1,zone_letter='C')
    assert abs(coords[0]-24297961)<1 and abs(coords[1]-3361639877625)<1

    # from_latlon tests

    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.from_latlon(89,-114)
    assert 'latitude out of range' in str(exception.value)

    with pytest.raises(OutOfRangeError) as exception:
        coords=utm.from_latlon(33,181)
    assert 'northing out of range' in str(exception.value)

    coords1=utm.from_latlon(-1,-90)
    coords2=utm.from_latlon(-1,-90,force_zone_number=17)
    assert coords1!=coords2

    assert utm.from_latlon(0,-81)==(500000.0, 0.0, 17, 'N')
    assert utm.from_latlon(60,10)[2]==32
    assert utm.from_latlon(80,9)[2]==31
    assert utm.from_latlon(80,21)[2]==33
    assert utm.from_latlon(80,33)[2]==35
    assert utm.from_latlon(80,42)[2]==37
    assert utm.latitude_to_zone_letter(-81)==None

