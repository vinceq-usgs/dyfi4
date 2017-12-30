# Test of readEvent.py (possibly redundant, fold in incoming test
# To run this test, you must be at the package root directory and run:
# pytest tests/test_aux.py

import pytest
from argparse import Namespace

testid='se609212'
configfile='tests/testconfig.yml'
testinput1='tests/data/feedContents.raw'
testinput2='tests/data/feedContents_2.raw'

def test_read(capsys):
    from app import readEvent
    from dyfi import RawDb,Config

    config=Config(configfile)
    rawdb=RawDb(config.db)

    # Test that this test works
    results=rawdb.query('event','eventid=?',testid+'_test')
    assert not results

    # Test initial table
    results=rawdb.query('event','eventid=?',testid)
    assert len(results)==1


    #--------------------------------
    # Inline test subroutine for convenience
    def _testrun(inputfile):
        args=Namespace(evid=testid,configfile=configfile,file=inputfile,raw=False,save=True)
        readEvent.main(args)
        return rawdb.query('event','eventid=?',testid)
    #--------------------------------

    # Test that new trigger does not create duplicate
    results=_testrun(testinput1)
    assert len(results)==1
    assert results[0]['mag']==5.8

    # Test that new trigger is updated
    results=_testrun(testinput2)
    assert len(results)==1
    assert results[0]['mag']==9.9

    # Now test remote reading from ComCat

    args=Namespace(evid=testid,configfile=configfile,file=None,raw=False,save=True)
    readEvent.main(args)

    output=capsys.readouterr()[0]
    for line in output.split('\n'):
        print(line)

    assert 'Virginia' in output

