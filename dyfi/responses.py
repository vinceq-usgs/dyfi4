"""

Process loop:

Download responses
For each response:
  Write to extended table
  If event doesn't exist in table:
    Save stub in event table (invisible=1)
    Run getEvent.py (separate process)
    

"""

import sys
import argparse
import os.path
import time

from .config import Config
from .db import Db

class Responses:

    def __init__(self,check,nofeed,configfile):

        config=Config(configfile)
        self.db=Db(config)
        self.responses=self.db.getResponses(check)
        self.processed=0

        if check:
            self.displayResponses()
            exit()

        if not self.responses:
            print('Responses: None found')
            return

        for response in self.responses:
            # save here
            self.processed+=1


    def displayResponses(self,check):
        print('Got %i events to process.' % len(self.events))
        event=self.events[0]
        print('Priority is event %s with %i responses.' %
            (event['eventid'],event['newresponses']))




    

