# To run this test, you must be at the package root directory and run:
# pytest tests/test_movie.py

import shutil
from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_run():
    import subprocess

    shutil.rmtree('./movie',ignore_errors=True)
    # 60 minute movie, each frame is 20 minutes
    status=subprocess.run(['app/makemovie.py',testid,'--tmax','60','--framelength','1200'])
    assert status


