"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

import sys
import argparse
import os.path
import time

from .config import Config
from .db import Db
from .comcat import Comcat

class Pending:

    def __init__(self,check,maxruns,configfile):

        config=Config(configfile)
        self.db=Db(config)
        self.events=self.db.getPendingEvents(minResponses=1)
        self.events=sorted(self.events,
            key=lambda x:x['newresponses'],
            reverse=True)
        self.processed=0

        if check:
            self.displayEvents()
            exit()

        if not self.events:
            print('Pending: No events found')
            return
     
        for event in self.events:
            evid=event['eventid']
            print('Pending: Running event',evid)
            time.sleep(5)
            self.processed+=1

            if maxruns>0 and self.processed>=maxruns:
                print('Pending: %i events done, stopping.' % maxruns)
                return



    def displayEvents(self):

        print('Got %i events to process.' % len(self.events))
        event=self.events[0]
        print('Priority is event %s with %i responses.' % 
            (event['eventid'],event['newresponses']))

