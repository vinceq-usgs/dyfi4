"""

Event
=====
        
"""

import json
import geojson

class Event:
    """
    
    :synopsis: Class for handling Event objects. This holds data about a particular earthquake referenced by the event ID. It requires an object holds data from the Db.loadEvent method.
    
    Creating an `Event` object will create a :py:obj:`db` instance 
    and load  event data from the database,
    and also load the :py:obj:`entry` list from the database.
    
    .. note:: 
        Access the data in this object with the keys in 
        :py:obj:`columns` as attributes, e.g. `event.evid`, 
        `event.region`, etc.

    .. data:: columns
    
    A list of all the columns in the event table.
    
    .. attribute:: raw
    
    A reference to the raw database output of the event data.
    
    .. attribute:: products
    
    A dict of productnames and refs to the :py:obj:`product` 
    objects created for this event.
    
    
"""

    columns=['eventid','region','source','mag','lat','lon','depth',
             'eventdatetime','eventlocaltime','loc','nresp','newresp',
             'max_intensity','code_version','event_version',
             'createdtime','process_timestamp','orig_id']

    
    def __init__(self,rawdata):

        if not rawdata:
            raise NameError('Event: Cannot create Event with no data')
            
        self.raw=rawdata
        self.entries=None
 
        for column in self.columns:
            if column in rawdata:
                self.__dict__[column]=rawdata[column]

                
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
   
        print('Event.update: disabled for now')
        return
   
    # Generic getattr method for parameters (no setattr)

    def __getattr__(self,name):
        if name not in self.columns:
            raise NameError('ERROR: Event got bad column '+name)
            
        if name in self.__dict__:
            return self.__dict__[name]
    
            
    def addProduct(self,product):
        """
        
        :synopsis: Attach a `product` to this event
        :param product: A :py:obj:`product` object
        :return: None
        
        Keep a list of Product objects attached to this product.
        
        .. note:: This will overwrite any previous Product objects of the same product type.
        
        """
        
        type=product.productType
        self.products[type]=product

    def getProducts(self):
        """
        
        :synopsis: Get all products for this event
        :return: dict of product types and products
        
        """
        
        return self.products
        
    def __str__(self):
        return 'M%s %s %s' % (self.mag,self.loc,self.eventdatetime)
  
    def __repr__(self):
        rawlist=[]
        for column in self.columns:
            if column in self.__dict__:
                val=str(self.__dict__[column])
                rawlist.append({column:val})

        return json.dumps(rawlist)
