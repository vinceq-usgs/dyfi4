import warnings
import sys
import os.path
import datetime

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
from dyfi import Db


class RunDb(Db):

    def __init__(self,config=None):
        Db.__init__(self,config)


    @staticmethod
    def timeago(t):
        """

        :synopsis: Compute a past datetime
        :param int t: Time interval in minutes
        :returns: :py:obj:`Datetime` object

        Returns the datetime from :py:attr:`t` minutes ago.

        """

        t0=datetime.datetime.now()
        tdelta=datetime.timedelta(minutes=t)
        tnew=t0-tdelta
        return(tnew)


################################
#
# Methods for loadEntries
#
################################

    def createStubEvent(self,evid,data):

       event=self.loadEvent(evid)
       if event or evid=='unknown':
           raise RuntimeError('RunDb.createStubEvent got existing or unknown event')

       createdtime=self.epochToString()
       stub={'table':'event','eventid':evid,'createdtime':createdtime}
       if data:
           for k,v in data.items():
               stub[k]=v
       self.save(stub)
       return True


    def setNewresponse(self,evid,value=1,increment=False):

        # This will increment the newresponses column of an event.
        # If the event does not exist, a stub will be created

        event=self.loadEvent(evid)
        if not event:
            invisible=1 if not value else 0
            print('db.setnewresponse: Creating stub',evid)
            return self.createStubEvent(evid,{'invisible':invisible,'newresponses':value})

        if increment and event['newresponses']:
            try:
                value+=int(event['newresponses'])
            except(ValueError): # pragma: no cover
                print('db.setNewresponse: WARNING: Could not parse old value for newresponses, ignoring')

        #print('db.setNewresponse: newresponses=%i, saving.' % value)
        event['newresponses']=value
        return self.save(event)

################################
#
# Methods for queueTriggers
#
################################

    @staticmethod
    def stringToAge(string):
        # Turn '2017-01-01 12:00:00' into seconds ago

        now=datetime.datetime.utcnow()
        dt=datetime.datetime.strptime(string,'%Y-%m-%d %H:%M:%S')

        return (now-dt).total_seconds()


    def getPendingEvents(self):

        table='event'
        clause='newresponses>0 and (invisible is null or invisible=0) order by cast(newresponses as int) desc'
        results=self.rawdb.query(table,clause)

        return results


    def deleteEvent(self,evid):
        event=self.loadEvent(evid)
        # Don't clobber previous value of invisible
        if event and 'invisible' in event and (event['invisible']=='0' or not event['invisible']):
            self.rawdb.updateRow('event',evid,'invisible',1)
        return


    def updateEventVersion(self,evid):

        timestamp=self.epochToString()
        self.rawdb.updateRow('event',evid,'process_timestamp',timestamp)
        self.rawdb.updateRow('event',evid,'ciim_version',1,increment=True)

        event=self.loadEvent(evid)
        timestamp=event['process_timestamp']
        ciim_version=event['ciim_version']

        print('Updated',evid,'to version',ciim_version,timestamp)


