# To run this test, you must be at the package root directory and run:
# pytest tests/test_util.py

import pytest
import shutil
from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'
entryfile='entry.server.ci37511872.1.1'
def test_util():
    import subprocess
    import shutil

    # Test loadEntries.py
    status=subprocess.run(['util/loadEntries.py','--check'],stdout=subprocess.PIPE)
    assert 'Got 1 responses in incoming' in str(status.stdout)

    status=subprocess.run(['util/loadEntries.py'],stdout=subprocess.PIPE)
    assert 'Processing' in str(status.stdout)

    # Put entry file back in incoming
    shutil.copy('tests/trashincoming/'+entryfile,'tests/incoming')

    # Test loadEntries.py
    status=subprocess.run(['util/queueTriggers.py','--check'],stdout=subprocess.PIPE)
    assert 'events to process.' in str(status.stdout)
    assert testid+' has' in str(status.stdout)

    status=subprocess.run(['util/queueTriggers.py','--maxruns','1'],stdout=subprocess.PIPE)
    assert 'Done with '+testid in str(status.stdout)

