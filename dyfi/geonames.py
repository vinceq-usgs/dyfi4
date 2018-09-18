import json
import geojson
import datetime

from .db import Db

class Geonames:
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

    columns=['utm','name']

    def __init__(self,utm,config=None,missing_ok=False):

        self.table='geonames'
        self.raw=None

        db=Db(config)
        row=db.loadGeoname(utm)
        blah

        elif isinstance(event,dict):
          evid=event['eventid']

        if not event and not missing_ok:
            raise RuntimeError('Cannot create Event with no data')

        self.raw=event

        for column in self.columns:
            val=event[column] if event and column in event else None
            setattr(self,column,val)

        if not self.eventdatetime:
            self.isStub=True


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

    def setattr(self,name,val):
        if name not in self.columns:
            raise ValueError('Event: Invalid column '+name)
        self.__setattr__(name,val)


    # Generic getattr method for parameters

    def __getattr__(self,name):

        # Change text datetime to Datetime object suitable for time arithmetic
        if name=='eventDateTime':
            dTime=self.eventdatetime
            tFormat='%Y-%m-%d %H:%M:%S'
            dTime=datetime.datetime.strptime(dTime,tFormat)
            dTime.replace(tzinfo=datetime.timezone.utc)
            return dTime

        if name!='duplicates' and name not in self.columns:
            raise ValueError('Event: Invalid column '+name)


    def __str__(self):
        return '[Event: %s M%s %s %s]' % (self.eventid,self.mag,self.loc,self.eventdatetime)


    def __repr__(self):
        rawlist=[]
        for column in self.columns:
            val=str(getattr(self,column))
            rawlist.append({column:val})

        return json.dumps(rawlist)
