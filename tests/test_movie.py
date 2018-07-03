# To run this test, you must be at the package root directory and run:
# pytest tests/test_movie.py

from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_run():
    import subprocess
    status=subprocess.run(['app/makemovie.py',testid,'--tmax','3600','--framelength','600'])
    assert status


