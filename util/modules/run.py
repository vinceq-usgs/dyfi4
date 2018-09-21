"""

Process loop:


Read event table for events with nresponses>n
Foreach event:
  Sort by nresponses
  For each event: run event

"""

import subprocess
import sys
import os

#sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
#from dyfi import Config

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'.')))
from modules.comcat import Comcat
from modules.runDb import RunDb
from modules.runEvent import RunEvent

class Run:

    noOverwriteColumns=['nresponses','newresponses','ciim_version','process_timestamp','orig_id']

    def __init__(self,config):

        self.config=config
        self.db=RunDb(config)
        self.duplicates=None
        self.event=None
        self.evid=None


    def loadComcat(self,evid,rawInput=None,raw=False,saveToFile=None):

        self.evid=evid
        comcat=Comcat(config=self.config,rawInput=rawInput)
        if raw:
            return comcat.event(evid,raw=True)
            
        inputJson=comcat.event(evid,saveToFile=saveToFile)

        if not inputJson or inputJson=='NOT FOUND':
            print('Run.loadComcat: No data for',evid)
            self.event='DELETED'
            return evid

        if inputJson=='DELETED':
            self.event='DELETED'
            return evid

        if inputJson=='BAD':
            self.event=None
            return None

        event=RunEvent.createFromContents(inputJson)
        self.event=event
        self.duplicates=event.duplicates
        if event.eventid!=evid:
            self.evid=event.eventid
            print('WARNING! WARNING! WARNING!')
            print('Event ID changed from %s to %s' % (evid,self.evid))
            print('WARNING! WARNING! WARNING!')

        return self.evid


    def updateEvent(self,save=True):

        event=self.event
        if not event:
            return

        if event=='DELETED' or event=='NOT FOUND':
            if save:
                print('Run.updateEvent: Got',event,'- deleting %s from database' % self.evid)
                self.db.deleteEvent(self.evid)
            return self.evid

        # Don't overwrite certain columns
        originalData=self.db.loadEvent(self.evid)
        if originalData:
            for k in (self.noOverwriteColumns):
                if originalData[k] is not None:
                    print('Setting',k,'to',originalData[k])
                    event.setattr(k,originalData[k])

        if save:
            self.db.save(event)
            print('Run.updateEvent: Saved %s with %i newresponses' % (event.eventid,event.newresponses or 0))

        return event.eventid


    def runEvent(self,evid=None,findDuplicates=True,norun=False,rawInput=None):

        print('--------------------------------')
        event=self.event

        if not evid and not event:
            raise RuntimeError('Run.runEvent: Called without evid or run.loadComcat')

        # 1. Check if Comcat gave delete or no ID
        if event=='DELETED' or event=='NOT FOUND':
            return

        # 2. If no update or update doesn't work, read database
        if evid and not event:
            raw=self.db.loadEvent(evid)
            if raw:
                self.event=RunEvent(raw)
                event=self.event

        # 2a. Check if no data
        if not event:
            print('Run.runEvent: No data found')
            return None

        # 2b. Check if stub
        if event.isStub: # pragma: no cover
            print('Run.runEvent: Cannot run on stub event.')
            return None

        # At this point, event should be populated
        evid=event.eventid

        # 3. Need loadComcat() to populate self.duplicates
        if self.duplicates:
            print('Run.runEvent: Moving duplicates.')
            self.moveDuplicates()

        # 4. Create event products
        if not norun:
            print('Updating event',evid)
            self.db.updateEventVersion(evid)

            print('Run.runEvent: Creating products for',evid)
            runCommand=self.config.executables['run'].split(' ')+[evid]
            subprocess.call(runCommand)


        # 5. Set new responses to zero and increment version
        if not norun:
            print('Run.runEvent: Updating event parameters.')
            self.db.setNewresponse(evid,value=0,increment=False)

        # 6. export to web
        if not norun and 'push' in self.config.executables:
            try: 
                runCommand=self.config.executables['push'].split(' ')+[evid]
                subprocess.call(runCommand)
            except FileNotFoundError:
                print('WARNING: No push command, ignoring.')

        return evid


    def moveDuplicates(self):
        if not self.duplicates:
            return

        db=self.db
        goodid=self.event.eventid
        print('Got duplicates:',self.duplicates)

        nMoved=0
        for dupid in self.duplicates:
            dupevent=RunEvent(dupid,missing_ok=True,config=self.config)
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


