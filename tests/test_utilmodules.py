from argparse import Namespace

testid='ci37511872'
configfile='tests/testconfig.yml'

import sys
import os
import json

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dyfi import Config

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../util')))
from modules.runEvent import RunEvent
from modules.runDb import RunDb

def test_runEvent():

    # Test blank data won't crash
    blankdata={}
    contents=RunEvent.createFromContents(blankdata)
    assert contents is None
    dups=RunEvent.readDuplicatesFromContents(blankdata)
    assert dups is None

    deleteddata=json.load(open('tests/data/feedContents.deleted','r'))
    contents=RunEvent.createFromContents(deleteddata)
    assert 'deleted' in contents


def test_runDb():
    import datetime

    # Test timeago
    interval=1 # minutes
    assert RunDb.timeago(interval)<datetime.datetime.now()

    # This will create a stub
    db=RunDb(Config(configfile))
    stubid='us1000abcd'
    db.setNewresponse(stubid,value=0)

    # Update the stub
    db.setNewresponse(stubid,value=1,increment=True)

    # Delete the stub
    db.deleteEvent(stubid)


