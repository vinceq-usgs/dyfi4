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

    noOverwriteColumns=['nresponses','newresponses','ciim_version','process_timestamp','orig_id']

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

        # Don't overwrite certain columns
        originalData=self.db.loadEvent(evid)
        if originalData:
            for k in (self.noOverwriteColumns):
                print('Setting',k,'to',originalData[k])
                event.setattr(k,originalData[k])

        if save:
            saved=self.db.save(event)
            print('Run.update: Saved %s with %i newresponses' % (event.eventid,event.newresponses or 0))

        return event.eventid


    def runEvent(self,evid,update=True,findDuplicates=True,test=False):

        print('--------------------------------')
        # 1. Update self.event from Comcat or file (and save)
        if update:
            print('Run.runEvent: Updating and saving this event.')
            self.update(evid)
            event=self.event
            # If authoritative ID changed, evid will change too

            # 1a. Check if Comcat gave delete or no ID
            if event=='DELETED' or event=='NOT FOUND':
                print('Run.runEvent: Got',event,'- deleting',evid)
                if not test:
                    self.db.deleteEvent(evid)
                return evid

        # 2. If update doesn't work, read database
        event=self.event
        if not event:
            raw=self.db.loadEvent(evid)
            # No guarantee that self.duplicates exist (unless
            # self.update() was run beforehand)
            if raw:
                self.event=Event(raw)
            event=self.event

        # 2a. Check if no data
        if not event: 
            print('Run.runEvent: No data found')
            return None

        # 2b. Some other Comcat error
        if isinstance(event,str):
            print('Run.runEvent: Got',event,'for',evid,'ignoring.')
            return None

        # 2c. Check if stub
        if event.isStub:
            print('Run.runEvent: Cannot run on stub event.')
            return None

      
       # 3. Update will populate event.duplicates 
        if self.duplicates:
            print('Run.runEvent: Moving duplicates.')
            if not test:
                self.moveDuplicates()

        # 4. Create event products
        print('Run.runEvent: Creating products.')
        if not test:
            proc=subprocess.Popen(['app/rundyfi.py',evid],stdout=subprocess.PIPE)
            results=proc.stdout.read().decode('utf-8')
            print(results)

        # 5. Set new responses to zero and increment version
        print('Run.runEvent: Updating event parameters.')
        if not test:
            self.db.setNewresponse(evid,value=0,increment=False)
            self.db.updateEventVersion(evid)

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
                startdatetime=self.event.eventdatetime)

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


