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
    status=subprocess.run(['app/rundyfi.py',testid])
    assert status
    status=subprocess.run(['app/makescreenshot.py','data/'+testid+'/dyfi_geo_10km.geojson'])
    assert status


