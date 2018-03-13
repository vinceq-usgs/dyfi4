import datetime
from .aggregate import aggregate
from .db import Db
from .entry import Entry

class Entries():
    """

    :synopsis: Handle a collection of entries and aggregation.
    :param str evid: (optional) event ID
    :param event: (optional) `Event` object
    :param str startdatetime: (optional) string of format 'YYYY-MM-DD HH:MM:SS'
    :param cdifilter: (optional) `filter` object for filtering data
    :param list rawentries: (optional) list of raw data (e.g. table rows)
    :param config: (optional) A `Config` object
    :param bool load:

    An Event object or startdatetime is necessary for db.loadEntries
    to know which extended tables to search.

    .. data:: entries

        A list of :py:obj:`Entry` objects.

    """

    def __init__(self,evid=None,event=None,startdatetime=None,cdifilter=None,rawentries=None,config=None,load=True):

        if evid:
            self.evid=evid
        elif event:
            self.evid=event.eventid
        else:
            raise RuntimeError('Entries: No evid or Event object specified')

        self.entries=[]
        self.filter=cdifilter

        if rawentries==None and load==True:
            db=Db(config)
            rawentries=db.loadEntries(evid=evid,event=event,startdatetime=startdatetime)

        count=0
        for row in rawentries:
            if isinstance(row,Entry):
                entry=row
            else:
                entry=Entry(row)
            self.entries.append(entry)
            count+=1


    def aggregate(self,name):
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

        Used to create the Time vs. Responses graph. The return value is a dict with the following values:

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

