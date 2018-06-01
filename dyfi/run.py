"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

import subprocess

from .config import Config
from .db import Db
from .event import Event
from .comcat import Comcat

class Run:

    def __init__(self,configfile):

        self.config=Config(configfile)
        self.db=Db(self.config)
        self.duplicates=None
        self.evid=None
        self.event=None


    def update(self,evid,raw=None,save=True,check=False):

        if not raw:
            comcat=Comcat(config=self.config)
            raw=comcat.event(evid)

        if not raw:
            print('Run.update: Could not get data for',evid)
            return

        event=Event.createFromContents(raw)
        self.event=event
        self.duplicates=self.event.duplicates

        self.evid=event.eventid
        if event.eventid!=evid: 
            print('WARNING! WARNING! WARNING!')
            print('Event ID changed from %s to %s' % (evid,event.eventid))
            print('WARNING! WARNING! WARNING!')

        if check:
            print(raw)
            return

        if save:
            # Don't overwrite newresponses
            originalData=self.db.loadEvent(evid)
            if originalData:
                event.newresponses=originalData['newresponses']
            saved=self.db.save(event)

        return self.evid


    def runEvent(self,evid,update=True,findDuplicates=True,test=False):

        # 1. Update self.event from Comcat or file (and save)
        if update:
            print('Run.runEvent: Updating and saving this event.')
            evid=self.update(evid)
            # If authoritative ID changed, evid will change too
        else:
            self.event=self.db.loadEvent(evid)

        if not self.event:
            print('Run.runEvent: No data found')
            return

        # 2. Update will populate event.duplicates, go through that
        if self.duplicates:
            print('Run.runEvent: Moving duplicates.')
            self.moveDuplicates()

        # 3.
        # call dyficontainer instead of running rundyfi.py
        print('Run.runEvent: Creating products.')
        proc=subprocess.Popen(['app/rundyfi.py',evid],stdout=subprocess.PIPE)
        results=proc.stdout.read().decode('utf-8')
        print(results)

        # 4. Set new responses to zero 
        print('Run.runEvent: Resetting newresponses.')
        self.db.setNewresponse(evid,value=0,increment=False)

        # 5. Set process_timestamp,increment ciim_version

        return evid


    def moveDuplicates(self):
        db=self.db
        goodid=self.evid

        if not self.duplicates:
            return

        print('Got duplicates:',self.duplicates)

        nMoved=0
        for dupid in self.duplicates:
            dupevent=Event(dupid,missing_ok=True,config=self.config)
            print('Run.moveDuplicates: Trying event',dupid)

            # If the dup event doesn't yet exist, create a stub
            # to warn future entries where to go

            if not dupevent.eventid:
                print('Run.moveDuplicates: Creating stub for',dupid)
                db.createStubEvent(dupid,{'good_id':goodid})
                continue

            # If dup event already exists, update its good_id

            if hasattr(dupevent,'good_id') and dupevent.good_id!=goodid:
                print('Run.moveDuplicates: Updating goodid for',dupid)
                db.rawdb.updateRow('event',dupid,'good_id',goodid)

            # Then find dup's entries and move them

            print('Run.moveDuplicates: Looking for entries for',dupid)
            entriesToMove=db.loadEntries(
                evid=dupid,
                loadSuspect=True,
                startdatetime=self.event.eventdatetime)

            if not entriesToMove:
                continue

            print('Run.moveDuplicates: Found',len(entriesToMove),'entries.')
            for e in entriesToMove:
                db.rawdb.updateRow(e['table'],e['subid'],'eventid',goodid)
                nMoved+=1

            db.setNewresponse(dupid,value=0,increment=False)

        if nMoved:
            print('Moved %i entries from %s to %s' % (nMoved,dupid,goodid))
            db.setNewresponse(goodid,value=nMoved,increment=True)



