"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

from .config import Config
from .db import Db
from .run import Run
from .lock import Lock


class Pending:

    def __init__(self,maxruns,configfile):

        config=Config(configfile)

        self.configfile=configfile # Store this for Run
        self.db=Db(config)
        self.conf=config.pending
        self.maxruns=maxruns
        self.events=[]
        self.eventsRun=0


    def displayEvents(self):
        self.events=self.db.getPendingEvents()

        print('Got %i events to process.' % len(self.events))
        nevents=len(self.events)
        if nevents==0:  return
        elif nevents>10: maxdisplay=10
        else: maxdisplay=nevents

        for i in range(0,maxdisplay):
            event=self.events[i]
            print('%i: %s has %i responses.' %
              (i,event['eventid'],event['newresponses']))


    def loop(self,test=False):
        maxruns=self.maxruns
        self.events=self.db.getPendingEvents()
        processed=False
        finishedEvents=[]

        while True:
            if maxruns and self.eventsRun>=maxruns:
                print('Pending: %i events processed' % maxruns)
                break

            # Refresh queue only if an event was run successfully
            if processed:
                self.events=self.db.getPendingEvents()
                processed=False

            if not self.events:
                break

            row=self.events.pop(0)
            evid=row['eventid']
            newresponses=row['newresponses']

            # Skip events currently running or recently processed
            if evid in finishedEvents:
                continue
            if self.isLocked(evid):
                print('Event',evid,'is locked, skipping.')
                continue
            if self.checkRunRecent(row):
                print('Event',evid,'run recently, skipping.')
                continue

            if test:
                print('Pending: loop test:',evid)
                runevid=evid
            else:
                print('Pending: loop processing %s with %i responses.' % (evid,newresponses))
                run=Run(self.configfile)
                runevid=run.runEvent(evid)

            finishedEvents.append(evid)

            if runevid:
                self.eventsRun+=1
                if runevid!=evid:
                    finishedEvents.append(runevid)

                # for test, iterate through all events
                if not test:
                    processed=True

        # Now either we hit maxruns or self.events is empty
        if self.eventsRun:
            print('Pending.loop: No more events.')
        else:
            print('.',end='',flush=True)
        return True


    @staticmethod
    def isLocked(evid):

        lock=Lock('rundyfi.'+evid,fail_ok=True,silent=True)
        if lock.success:
            lock.removeLock()
            return False

        return True


    def checkRunRecent(self,row):

        if not 'process_timestamp' in row or not row['process_timestamp']:
            print('pending.checkRunRecent: WARNING: No process timestamp for event',ro['eventid'])
            return None

        age=self.db.stringToAge(row['process_timestamp'])
        if age<self.conf['delay']:
            return True

        return False

