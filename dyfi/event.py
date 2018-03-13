import json
import geojson
import datetime

from .db import Db

class Event:
    """

    :synopsis: Class for handling Event objects
    :param event: A :py:class:`dyfi.Event` object or event ID string
    :param config: A :py:class:`dyfiConfig` object

    This contains the parameters of a particular earthquake referenced by the event ID. It requires an object that holds data from the Db.loadEvent method, or an event ID string (in which case it loads the event data from the database).

    .. note::
        Access the data in this object with the keys in
        :py:obj:`columns` as attributes, e.g. `event.evid`,
        `event.region`, etc.

    .. data:: columns

    A list of all the columns in the event table.

    .. attribute:: raw

    A reference to the raw database output of the event data.

"""

    columns=['eventid','region','source','mag','lat','lon','depth',
             'eventdatetime','eventlocaltime','loc',
             'nresponses','newresponses',
             'max_intensity','code_version','event_version',
             'createdtime','process_timestamp','orig_id','good_id']


    def __init__(self,event,config=None):

        self.table='event'

        if isinstance(event,str):
          evid=event
          db=Db(config) 
          event=db.loadEvent(evid)

        elif isinstance(event,dict):
          evid=event['eventid']

        if not event:
            raise RuntimeError('Cannot create Event with no data')

        self.raw=event

        for column in self.columns:
            val=event[column] if column in event else None
            setattr(self,column,val)


    def toGeoJSON(self):
        props={}
        rawdata=self.raw
        for key,val in rawdata.items():
            if key=='lat':
                latitude=val
            elif key=='lon':
                longitude=val
            else:
                props[key]=val

        feature=geojson.Feature(
            geometry=geojson.Point((latitude,longitude)),
            properties=props,
            id=rawdata['eventid']
            )

        return feature

    @classmethod
    def update(cls): # pragma: no cover
        """

        :synopsis: Save the contents of this Event object to the DB event table.
        :returns: none

        """

        print('TODO: Event.update: disabled for now')
        return


    # Generic getattr method for parameters (no setattr)

    def __getattr__(self,name):

        # Change text datetime to Datetime object suitable for time arithmetic
        if name=='eventDateTime':
            dTime=self.eventdatetime
            tFormat='%Y-%m-%d %H:%M:%S'
            dTime=datetime.datetime.strptime(dTime,tFormat)
            dTime.replace(tzinfo=datetime.timezone.utc)
            return dTime

        if name not in self.columns:
            raise ValueError('Event: Invalid column '+name)


    def __str__(self):
        return '[Event: %s M%s %s %s]' % (self.eventid,self.mag,self.loc,self.eventdatetime)


    def __repr__(self):
        rawlist=[]
        for column in self.columns:
            val=str(getattr(self,column))
            rawlist.append({column:val})

        return json.dumps(rawlist)


