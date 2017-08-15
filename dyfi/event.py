"""

Event
=====
        
"""

import json
import geojson

from .db import Db

class Event:
    """
    
    :synopsis: Class for handling Event objects. This holds data about a particular earthquake referenced by the event ID. It requires an object that holds data from the Db.loadEvent method, or an event ID string (in which case it loads the data itself).
    
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
             'eventdatetime','eventlocaltime','loc','nresp','newresp',
             'max_intensity','code_version','event_version',
             'createdtime','process_timestamp','orig_id']

    
    def __init__(self,data,config=None):

        if not data:
            raise NameError('Event: Cannot create evid with no data')
       
        if isinstance(data,str):
          evid=data
          db=Db(config)
          data=db.loadEvent(evid)

        else:
          evid=data['eventid']
    
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

                
    def update(self): # pragma: no cover
        """
    
        :synopsis: Save the contents of this Event object to the DB event table.
        :returns: none
        
        """
   
        print('TODO: Event.update: disabled for now')
        return
   
    # Generic getattr method for parameters (no setattr)

    def __getattr__(self,name):
        if name not in self.columns:
            raise NameError('ERROR: Event got bad column '+name)
            
        if name in self.__dict__:
            return self.__dict__[name]
    
            
    def __str__(self):
        return 'M%s %s %s' % (self.mag,self.loc,self.eventdatetime)

  
    def __repr__(self):
        rawlist=[]
        for column in self.columns:
            if column in self.__dict__:
                val=str(self.__dict__[column])
                rawlist.append({column:val})

        return json.dumps(rawlist)
