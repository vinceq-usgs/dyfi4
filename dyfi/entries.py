from .aggregate import aggregate
from .db import Db
import datetime

class Entries():
    """

    :synopsis: Handle a collection of entries and aggregation.
    :param list rawdata: optional list of raw data (e.g. table rows)

    The Event object is necessary/useful because db.loadEntries
    needs the object's event date attribute to calculate which
    extended tables to search.

    .. data:: entries

        A list of :py:obj:`Entry` objects.

    """

    # TODO: Capability of handling raw entries instead of evid
    def __init__(self,evid=None,event=None,filter=None,rawentries=None,config=None,load=True):

        if evid:
            self.evid=evid
        elif event:
            self.evid=event.eventid
        else:
            raise RuntimeError('Entries: No evid or Event object specified')

        self.entries=[]
        self.filter=filter

        if rawentries==None and load==True:
            db=Db(config)
            rawentries=db.loadEntries(evid=evid,event=event)

        count=0
        for row in rawentries:
            if isinstance(row,Entry):
                entry=row
            else:
                entry=Entry(row)
            self.entries.append(entry)
            count+=1


    def aggregate(self,name,force=False):
        """

        :synopsis: Aggregate the entry data in this object
        :param str name: The name of this aggregation
        :returns: A `GeoJSON` :py:obj:`FeatureCollection`
        
        A wrapper to :py:obj:`Aggregate.aggregate`. The :py:attr:`name` indicates the kind of aggregation (e.g. 'geo_1km' or 'geo_10km').

        """

        locations=aggregate(self.entries,name)
        if not self.filter:
            return locations

        print('Entries: aggregate has',len(locations.features),'locations.')
        goodLocations=[]
        for location in locations.features:
            bad=self.filter(location)
            if not bad:
               goodLocations.append(location) 

        locations.features=goodLocations
        print('Entries: aggregate now has',len(locations.features),'locations.')
        return locations


    def getTimes(self,datatype):
        """

        :synopsis: Create a list of entry times from a list of entries
        :param str datatype: Usually 'time'
        :returns: A dict of times data

        The return value is a dict with the following values:

        =====    =============================================
        id       'numresp'
        name     Same as :py:attr:`datatype`
        data     A sorted list of :py:obj:`datetime` objects
        =====    =============================================

        """

        entries=self.entries
        times=[]
        for entry in entries:
            entryTime=entry.time_now
            dTime=datetime.datetime.strptime(entryTime,
                '%Y-%m-%d %H:%M:%S')
            dTime.replace(tzinfo=datetime.timezone.utc)
            times.append(dTime)

        times.sort()
        data={
            'id':'numresp',
            'name':datatype,
            'data':times
        }
        return data


    def __len__(self):
        return len(self.entries)


    def __iter__(self):
        return self.entries.__iter__()


    def __str__(self):
        text='[Entries: evid:%s, responses:%i]' % (
            self.evid,len(self.entries))
        return text


    # TODO: Make this into GeoJSON representation
    def __repr__(self):
        text=''
        for entry in self.entries:
          text+=repr(entry)+'\n'

        text='Entries['+text[:-1]+']'
        return text


class Entry():
    """

    :synopsis: Class for handling user questionnaire responses
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
        'confidence','version','citydb','cityid'
    ]

    cdicolumns=[
        'subid','table','latitude','longitude','felt','other_felt',
        'motion','reaction','stand','shelf','picture',
        'furniture','damage'
    ]

    def __init__(self,rawdata):
        self.table='extended'

        for column in Entry.columns:
            if column in rawdata.keys():
                self.__dict__[column]=rawdata[column]
            else:
                self.__dict__[column]=None


    def __str__(self):
        text='[Entry: subid:%s, intensity:%s]' % (
            self.subid,self.user_cdi)
        return text


    def __repr__(self):
        text=''
        for column in Entry.columns:
            if self.__dict__[column]:
                val=str(self.__dict__[column])
                text=text+column+':'+val+','

        text='Entry('+text[:-1]+')'
        return text

