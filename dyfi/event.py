import json
import geojson
import datetime
import time

from .db import Db

class Event:
    """

    :synopsis: Class for handling Event objects
    
    This holds data about a particular earthquake referenced by the event ID. It requires an object that holds data from the Db.loadEvent method, or an event ID string (in which case it loads the data itself).

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


    def __init__(self,data,config=None):
        self.db=None
        self.table='event'

        if isinstance(data,str):
          evid=data
          self.db=Db(config)
          data=self.db.loadEvent(evid)

        elif isinstance(data,dict):
          evid=data['eventid']

        if not data:
            raise RuntimeError('Cannot create Event with no data')

        self.raw=data

        for column in self.columns:
            if column in data:
                self.__dict__[column]=data[column]


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
            raise NameError('ERROR: Event got bad column '+name)


    def __str__(self):
        return '[Event: %s M%s %s %s]' % (self.eventid,self.mag,self.loc,self.eventdatetime)


    def __repr__(self):
        rawlist=[]
        for column in self.columns:
            if column in self.__dict__:
                val=str(self.__dict__[column])
                rawlist.append({column:val})

        return json.dumps(rawlist)


    @classmethod
    def createFromContents(self,contents):
        rawdata={'id':contents['id']}
                
        relevant=['place','time','mag','ids','net']
        for key in relevant:
            rawdata[key]=contents['properties'][key]

        coords=['lon','lat','depth']
        rawdata.update(zip(coords,contents['geometry']['coordinates']))

        
# calculate: eventdatetime nresp newresp max_intensity createdtime process_timestamp
# ignore: eventlocaltime code_version event_version orig_id

        rawdata['eventdatetime']=Db.epochToString(rawdata['time']/1000)
        rawdata['createdtime']=Db.epochToString()

        conversion={
            'eventid':'id',
            'loc':'place',
            'source':'net'
        }

        converted={}
        for key in self.columns:
            if key in rawdata:
                converted[key]=rawdata[key]
            elif key in conversion:
                converted[key]=rawdata[conversion[key]]
            else:
                converted[key]=None

        event=Event(converted)
        return event

