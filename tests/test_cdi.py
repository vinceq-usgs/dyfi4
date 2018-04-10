# To run this test, you must be at the package root directory and run:
# pytest tests/test_cdi.py

import pytest

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_cdi():
  from dyfi import Entry,cdi,aggregate

  single=Entry({'felt':1,'furniture':1})
  user_cdi=cdi.calculate(single)
  assert user_cdi>=2 or user_cdi==1

  # test if entry has a missing required column

  missing=Entry({'furniture':1})
  assert cdi.calculate(missing)==2

  single=Entry({'felt':'a bad value'})
  with pytest.raises(ValueError) as exception:
      cdi.calculate(single)
  assert 'invalid literal' in str(exception.value)

