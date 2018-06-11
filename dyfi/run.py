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
        self.event=None


    def update(self,evid,raw=False,save=True,inputJson=None):

        if not inputJson:
            comcat=Comcat(config=self.config)
            inputJson=comcat.event(evid,raw=raw)

        if not inputJson or inputJson=='NOT FOUND':
            print('Run.update: Could not get data for',evid)
            return evid

        if inputJson=='DELETED':
            self.event='DELETED'
            return evid

        event=Event.createFromContents(inputJson)
        self.event=event
        self.duplicates=self.event.duplicates

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


    def runEvent(self,evid,update=True,findDuplicates=True,test=False,norun=False):

        print('--------------------------------')
        event=self.event

        # 1. Update self.event from Comcat or file (and save)
        if update:
            print('Run.runEvent: Updating and saving this event.')
            self.update(evid)
            event=self.event

            # 1a. Check if Comcat gave delete or no ID
            if event=='DELETED' or event=='NOT FOUND':
                print('Run.runEvent: Got',event,'- deleting',authid)
                if not test:
                    self.db.deleteEvent(authid)
                return authid

        # 2. If no update or update doesn't work, read database
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
            print('Run.runEvent: Got',event,'for',authid,'ignoring.')
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

        # 4. Create event products. At this point switch to authoritative id
        evid=event.eventid
        if not test and not norun:
            self.db.updateEventVersion(evid)
            print('Run.runEvent: Creating products for',evid)
            runCommand=self.config.executables['run'].split(' ')+[evid]
            proc=subprocess.call(runCommand)

        # 5. Set new responses to zero and increment version
        print('Run.runEvent: Updating event parameters.')
        if not test:
            self.db.setNewresponse(evid,value=0,increment=False)

        # 6. export to web
        if not test:
            runCommand=self.config.executables['push'].split(' ')+[evid]
            proc=subprocess.call(runCommand)

        return evid


    def moveDuplicates(self):
        db=self.db
        goodid=self.event.eventid

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


