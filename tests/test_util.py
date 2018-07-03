# To run this test, you must be at the package root directory and run:
# pytest tests/test_util.py

import pytest
import shutil
from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_util():
    import subprocess
    import shutil
    import os

    origDir='tests/orig.incoming'
    incomingDir='tests/incoming'

    # Create incoming directory
    os.makedirs(incomingDir,exist_ok=True)
    for name in os.listdir(origDir):
        fullname=os.path.join(origDir,name)
        if (os.path.isfile(fullname)):
            shutil.copy(fullname,incomingDir)

    # Test loadEntries.py
    status=subprocess.run(['util/loadEntries.py','--check'],stdout=subprocess.PIPE)
    assert 'Got 4 responses in incoming' in str(status.stdout)

    # Test maxfiles flag
    status=subprocess.run(['util/loadEntries.py','--maxfiles','1'],stdout=subprocess.PIPE)
    assert 'Processed 1 files, stopping.' in str(status.stdout)

    status=subprocess.run(['util/loadEntries.py'],stdout=subprocess.PIPE)
    assert 'Processing' in str(status.stdout)

    # Test loadEntries.py
    status=subprocess.run(['util/queueTriggers.py','--check'],stdout=subprocess.PIPE)
    assert 'events to process.' in str(status.stdout)
    assert testid+' has' in str(status.stdout)

    status=subprocess.run(['util/queueTriggers.py','--maxruns','1'],stdout=subprocess.PIPE)
    assert 'Done with '+testid in str(status.stdout)

    status=subprocess.run(['util/updateEvent.py',testid,'--trigger'],stdout=subprocess.PIPE)
    assert 'Done with '+testid in str(status.stdout)

