"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

from .config import Config
from .db import Db
from .event import Event

class Pending:

    def __init__(self,maxruns,configfile):

        self.db=Db(Config(configfile))
        self.maxruns=maxruns
        self.events=self.db.getPendingEvents()
        self.eventsRun=0


    def loop(self):
        maxruns=self.maxruns
        for row in self.events:

            if maxruns>0 and self.eventsRun>=maxruns:
                print('Pending: %i events processed' % maxruns)
                break

            if self.processEvent(row):
                 self.eventsRun+=1

        # Continue processing here
        return True


    def processEvent(self,row):

        event=Event(row)
        evid=event.eventid
        print('Pending: Running event',evid)

        # TODO: check duplicate entries and grab them

        1. if good event, 
        #newevid=self.moveDuplicates(evid)
        #if newevid!=evid:
        #    print('Pending: recalculating loop after this.')
        #    evid=newid
        #    recalculate=True


        #db.resetNewResponses(evid)

        return True


    def displayEvents(self):

        print('Got %i events to process.' % len(self.events))
        if len(self.events)==0:
            return

        event=self.events[0]
        print('Priority is event %s with %i responses.' %
            (event['eventid'],event['newresponses']))

