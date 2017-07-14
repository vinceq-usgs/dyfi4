"""

Maps
====
    
"""

class Maps():
    """
    
    :synopsis: Handle a set of maps.
    :param list rawdata: a list of raw data from the maps DB table

    .. data:: maplist
    
        A list of Map objects.
        
    """
    
    def __init__(self,rawlist):
        
        maplist={}
        
        if not rawlist:
            self.maplist=maplist
            return
        
        for row in rawlist:
            newmap=Map(row)
            mapid=newmap.mapid
            maplist[mapid]=newmap

        # This might be blank. That's okay
        self.maplist=maplist

        
class Map():
    """

    :synopsis: Handle parameters for a single map. 
    :param dict rawdata: raw data from one row of the maplist table
    
    .. note::
        Access the data in this object with the keys in 
        `Maplist.columns` as attributes,  e.g. `maplist.eventid` 
        or `maplist.lat_offset`.
        
    .. data:: columns
    
        A list of all the columns in the extended tables.
        
    """
    
    columns=[
        'subid','eventid','mapid','name',
        'proj','cdidata','proj',
        'center_lat','center_lon','lat_offset','lon_offset','lat_span',
        'lon_span','flags',
        'topo','topo_res','addtextfile','obsfile',
        'list','description','geocode_div','minresp',
        'table'
    ]
        
    def __init__(self,rawdata):

        self.rawdata=rawdata
        for column in rawdata:
            self.__dict__[column]=rawdata[column]
 
    def __str__(self):
        text='Map %s %s "%s"' % (self.subid,self.mapid,self.name)
        return text    

                
                
                
                
        
                

                
        
