"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

from .config import Config
from .db import Db

class Pending:

    def __init__(self,maxruns,configfile):

        config=Config(configfile)
        self.db=Db(config)
        self.maxruns=maxruns
        self.events=[]
        self.eventsRun=0


    def countEvents(self):
        events=self.db.getPendingEvents()
        events=sorted(events,
           key=lambda x:x['newresponses'],
           reverse=True)
        self.events=events
        return self.events


    def loop(self):
        maxruns=self.maxruns
        while True:
            if not self.loopEvents():
                print('Pending: No events found')
                return

            if maxruns>0 and self.eventsRun>=maxruns:
                print('Pending: %i events processed' % maxruns)
                return


    def loopEvents(self):
        self.countEvents()
        if not self.events: return

        self.events=[x['eventid'] for x in self.events]

        recalculate=False
        for evid in self.events:
            print('Pending: Running event',evid)

            newevid=self.moveDuplicates(evid)
            if newevid!=evid:
                print('Pending: recalculating loop after this.')
                evid=newid
                recalculate=True

            # TODO: check duplicate entries and grab them

            db.resetNewResponses(evid)
            self.eventsRun+=1

            if recalculate: break
            if self.maxruns>0 and self.eventsRun>=maxruns: break

        return True


    def displayEvents(self):

        print('Got %i events to process.' % len(self.events))
        if len(self.events)==0:
            return

        event=self.events[0]
        print('Priority is event %s with %i responses.' %
            (event['eventid'],event['newresponses']))

