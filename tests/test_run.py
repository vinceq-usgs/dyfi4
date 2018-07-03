# To run this test, you must be at the package root directory and run:
# pytest tests/test_run.py

import pytest
import shutil
from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_lock():
    from dyfi import Lock
    lock=Lock('testlock')
    trylock=Lock('testlock',fail_ok=True)
    assert trylock.success is False

    with pytest.raises(SystemExit):
        Lock('testlock')
    lock.removeLock()


def test_run():
    import subprocess

    # Test rundyfi.py
    status=subprocess.run(['app/rundyfi.py',testid],stdout=subprocess.PIPE)
    assert 'Done with %s' % testid in str(status.stdout)

    # Test makescreenshot.py
    inputfile='data/%s/dyfi_geo_10km.geojson' % testid
    outputfile='data/%s/screenshot.png' % testid
    status=subprocess.run(['app/makescreenshot.py',inputfile,outputfile],stdout=subprocess.PIPE)
    assert 'Created %s' % outputfile in str(status.stdout)


