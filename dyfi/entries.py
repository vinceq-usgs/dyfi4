"""

Entries
=======

    
"""

from .aggregate import aggregate


class Entries():
    """
      
    :synopsis: Handle a collection of entries and aggregation.
    :param list rawdata: a list of raw data from the extended DB table

    .. data:: entries

        A list of Map objects.

    """

    def __init__(self,rawlist):

        self.entriesdict={}
        self.entrieslist=[]
        self.aggregated={}

        if not rawlist:
            self.entries=entries
            return

        for row in rawlist:
            entry=Entry(row)
            subid='%s,%s' % (entry.subid,entry.table)
            self.entriesdict[subid]=entry
            self.entrieslist.append(entry)
    
    def __len__(self):        
        return len(self.entrieslist)

    
    def __iter__(self):
        return self.entrieslist.__iter__()

    
    def aggregate(self,name,force=False):
        if name in self.aggregated and not force:
            return self.aggregated[name]

        aggregated=aggregate(self.entrieslist,name)
        self.aggregated[name]=aggregated
        return aggregated
        
        
class Entry():
    """

    :synopsis: Class for handling user questionnaire responses. 
    :param dict rawdata: raw data from one row of an extended table
    
    .. warning:: 
        An Entry object contains raw data and may have PII 
        or invalid location data. DO NOT EXPORT `Entry` OBJECTS!

    .. note::
        Access the data in this object with the keys in 
        `Entry.columns` as attributes,  e.g. `entries.eventid` 
        or `event.felt`.
        
    .. data:: columns
    
        A list of all the columns in the extended tables.
        
    .. data:: cdicolumns
    
        A subset of extended columns used for intensity calculation.

    """
    
    columns=[
        'subid','eventid','orig_id','suspect',
        'region','usertime','time_now',
        'latitude','longitude','geo_source','zip','zip_4',
        'city','admin_region','country',
        'street','name','email','phone',
        'situation','building','asleep',
        'felt','other_felt','motion','duration','reaction',
        'response','stand','sway','creak','shelf',
        'picture','furniture','heavy_appliance','walls','slide_1_foot',
        'd_text','damage','building_details','comments','user_cdi',
        'city_latitude','city_longitude','city_population',
        'zip_latitude','zip_longitude','location','tzoffset',
        'confidence','version','citydb','cityid',
        'table'
    ]

    cdicolumns=[
        'subid','table','latitude','longitude','felt','other_felt',
        'motion','reaction','stand','shelf','picture',
        'furniture','damage'
    ]

    def __init__(self,rawdata):

        for column in rawdata:
            if column in Entry.columns or '__' in column:
                self.__dict__[column]=rawdata[column]
            else:
                print('WARNING: Entry: Unknown column',column)
                                
    def __repr__(self):
        text=''
        for column in ('subid','user_cdi'):
            if column in self.__dict__:
                val=str(self.__dict__[column])
                text=text+column+':'+val+','
                
        text='Entry('+text[:-1]+')'
        return text    

                
                
                
                
        
                

                
        
