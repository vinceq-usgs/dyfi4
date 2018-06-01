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


    def update(self,evid,raw=False,save=True,inputJson=None):

        if not inputJson:
            comcat=Comcat(config=self.config)
            inputJson=comcat.event(evid,raw=raw)

        if not inputJson or inputJson=='NOT FOUND':
            print('Run.update: Could not get data for',evid)
            return None

        if inputJson=='DELETED':
            self.event='DELETED'
            return None

        event=Event.createFromContents(inputJson)
        self.event=event
        self.duplicates=self.event.duplicates

        self.evid=event.eventid
        if event.eventid!=evid: 
            print('WARNING! WARNING! WARNING!')
            print('Event ID changed from %s to %s' % (evid,event.eventid))
            print('WARNING! WARNING! WARNING!')

        if save:
            # Don't overwrite newresponses
            originalData=self.db.loadEvent(evid)
            if originalData:
                event.newresponses=originalData['newresponses']
            saved=self.db.save(event)
            print('Run.update: Saved %s with %i newresponses' % (event.eventid,event.newresponses))

        return event.eventid


    def runEvent(self,evid,update=True,findDuplicates=True,test=False):

        # 1. Update self.event from Comcat or file (and save)
        if update:
            print('Run.runEvent: Updating and saving this event.')
            self.update(evid)
            # If authoritative ID changed, evid will change too

        if not self.event:
            raw=self.db.loadEvent(evid)
            # No guarantee that self.duplicates exist (unless
            # self.update() was run beforehand)
            if raw:
                self.event=Event(raw)

        event=self.event

        if not event: 
            print('Run.runEvent: No data found')
            return None

        # Check if stub
        if isinstance(event,Event) and event.isStub:
            print('Run.runEvent: Cannot run on stub event.')
            return None

        if event=='DELETED' or event=='NOT FOUND':
            print('Run.runEvent: Got',event'- deleting',evid)
            if not test:
                self.deleteEvent(evid)
            return evid

        # 2. Update will populate event.duplicates 
        if self.duplicates:
            print('Run.runEvent: Moving duplicates.')
            if not test:
                self.moveDuplicates()

        # 3. Create event products
        print('Run.runEvent: Creating products.')
        if not test:
            proc=subprocess.Popen(['app/rundyfi.py',evid],stdout=subprocess.PIPE)
            results=proc.stdout.read().decode('utf-8')
            print(results)

        # 4. Set new responses to zero 
        print('Run.runEvent: Resetting newresponses.')
        if not test:
            self.db.setNewresponse(evid,value=0,increment=False)

        # 5. Set process_timestamp,increment ciim_version

        # 6. export to web

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
                startdatetime=event.eventdatetime)

            if not entriesToMove:
                continue

            print('Run.moveDuplicates: Found',len(entriesToMove),'entries.')
            for e in entriesToMove:
                db.rawdb.updateRow(e['table'],e['subid'],'eventid',goodid)
                nMoved+=1

            db.setNewresponse(dupid,value=0,increment=False)
            db.rawdb.updateRow('event',dupid,'invisible',1)

        if nMoved:
            print('Moved %i entries from %s to %s' % (nMoved,dupid,goodid))
            db.setNewresponse(goodid,value=nMoved,increment=True)

        return nMoved 


    def deleteEvent(self,evid):
        db=self.db

        event=db.loadEvent(evid)
        if 'invisible' in event and (event['invisible']=='0' or not event['invisible']):
            db.rawdb.updateRow('event',evid,'invisible',1)
        return

