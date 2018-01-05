# To use MySQL,
# 1. change line 6 from .rawDbSqlite to .rawDbMysql
# 2. same for dyfi/__init__.py

import warnings
from .rawDbSqlite import RawDb

import geojson
import datetime

class Db:
    """

    :synopsis: Open a connection to access the DYFI database
    :param config: (optional) :py:class:`Config` object

    This connection is required to run any database queries.
    The database is currently implemented in SQLite. (Subject to change)

    .. note:: To change to the database implementation to MySQL, see the heading of this module.

    .. data:: tables

        A list of all tables (including extended tables).

    .. data:: exttables

        A list of all the extended tables.

    .. data:: latesttable

        The name of the latest extended table
        (should be the current year, e.g. "extended_2016").

    .. data:: EXT_MINYR

       The year of the earliest named extended table. Previous entries are contained in the table 'extended_pre'.

    .. data:: EXT_MINYR

       The year of the latest defined extended table.

    """

    # TODO:
    # create table 'extended' with up to two years of latest entries
    # automatically calculate tables: ...2014,2015,extended
    # calculate MAXYR automatically
    # when searching dates, get the correct tables automatically

    EXT_MINYR=2003;
    EXT_MAXYR=None;

    def __init__(self,config=None):

        Db.EXT_MAXYR=datetime.datetime.utcnow().year

        self.rawdb=RawDb(config.db)
        self.params=config.db
        self.tables=['event','maps']
        self.exttables=['extended_'+str(x) for x in
            (['pre'] + list(range(self.EXT_MINYR,self.EXT_MAXYR+1)))]
        self.latesttable=self.exttables[-1]
        self.event=''

        self.tables.extend(self.exttables)


    def save(self,obj,table=None):
        """

        :synopsis: Save object to the database table
        :param obj: Data object, see below
        :returns: Success or failure

        """

        if hasattr(obj,'table'):
            table=obj.table

        if not table:
            raise ValueError('Cannot save, table not specified')

        if 'extended' in table:
            table=self.getExtendedTablesByDatetime(obj.time_now)[0]

        if table=='event' or 'extended' in table:
            return self.rawdb.save(table,obj)

        else:
            print('Db: Unknown object',obj)
            return


    def loadEvent(self,evid):
        """

        :synopsis: Read database for an event
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns: dict suitable for input to an :py:obj:`Event` instance

        This is mostly a wrapper to the `RawDb` :py:meth:`query` method.

        """

        table='event'
        clause='eventid=?'
        results=self.rawdb.query(table,clause,evid)
        if not results or len(results)==0:
            return

        if len(results)>1: # pragma: no cover
            warnings.warn(UserWarning('Multiple events found, using only the first'))

        results=results[0]
        return results


    def loadMaps(self,evid):
        """

        :synopsis: Get a list of maps for an event.
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns: list of rows suitable for input to an :py:obj:`Maps` instance

        This is mostly a wrapper to the `RawDb` :py:meth:`query` method.

        Each item in the return list is a dict with keys
        being columns to the maps table.

        """

        table='maps'
        clause='eventid=?'
        results=self.rawdb.query(table,clause,evid)
        if not results:
            return

        # We expect multiple rows
        return results


    def loadEntries(self,evid=None,event=None,
                    table=None,startdatetime=None,
                    querytext=None):
        """

        :synopsis: Search the extended tables for entries matching a query.
        :param str evid: (optional) eventid
        :param Event event: (optional) Event object
        :param table: (optional) table or tables
        :param startdatetime: optional datetime to start search
        :param str querytext: optional clause(s)
        :returns: list of entries suitable for aggregation

        This is mostly a wrapper to the :py:obj:`rawDBSqlite` :py:obj:`query` object.

        It also figures out which extended tables to search,
        depending on the date of the event, using
        :py:obj:`getExtendedTablesByDatetime`.

        For valid values of parameter :py:attr:`table` see the :py:meth:`checkTables` method.

        The optional query parameter is a string of SQL `WHERE` clauses
        (e.g. 'suspect=0 OR suspect is null').

        Each item in the return list is a dict of entries from the extended tables, plus an additional key `table` that contains the name of the source extended table (see :py:obj:`query`).
        """

        # First, figure out which tables to check

        if table:
          table=self.checkTables(table)

        else:
            if startdatetime:
                table=self.getExtendedTablesByDatetime(startdatetime)
            elif event:
                table=self.getExtendedTablesByDatetime(event.eventdatetime)
            else:
                print('Db: WARNING: db.loadEntries using latest table only')
                table=self.latesttable

        # Second, figure out which eventid to query

        myclauses=[]
        mysubs=[]
        if querytext:
            myclauses.append(querytext)

        if event and not evid:
            evid=event.eventid

        if evid:
            myclauses.append('eventid=?')
            mysubs.append(evid)

        if startdatetime:
            myclauses.append('time_now>=?')
            mysubs.append(startdatetime)

        # Finally, combine queries

        if myclauses:
            querytext=' AND '.join(myclauses)

        results=self.rawdb.query(table,querytext,mysubs)
        return results


    def checkTables(self,table):
        """

        :synopsis: Check that the table or tables exist
        :param table: Table (str or int) or list of tables
        :returns: list of table names

        The :attr:`table` parameter accepts a single table, a comma-separated list of tables, or a list of tables. Each table is either the table name, a year (for extended tables), or 'latest' or 'all' for extended tables.

        The return value is a list of proper table names ('2016' will be converted to 'extended_2016', etc.) If any of the tables don't exist, a ValueError is returned.

        """

        if table=='all':
            return self.exttables

        if isinstance(table,str) and ',' in table:
            tables=table.split(',')

        elif not isinstance(table,list):
            tables=[table]
        else:
            tables=table

        outtables=[]
        for table in tables:
            if isinstance(table,int):
                table='extended_'+str(table)

            if table=='latest':
                table=self.latesttable

            if table in self.tables:
                outtables.append(table)

            elif 'extended_'+table in self.tables:
                outtables.append('extended_'+table)

            else:
                raise ValueError('Db: no such table '+table)

        return outtables


    @classmethod
    def timeago(cls,t):
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


    @classmethod
    def row2geojson(cls,row):
        """

        :synopsis: Convert a database entry row into a GeoJSON object
        :param dict row: A dict entry
        :returns: :py:obj:`GeoJSON` dict

        """
        lat=row['latitude']
        lon=row['longitude']
        if not lat or not lon: # pragma: no cover
            print('Db: Unable to get lat/lon for this row')
            return
        pt=geojson.Point((lon,lat))
        props={}
        for key,val in row.items():
            if key=='latitude' or key=='longitude':
                continue
            if val=='null' or val=='':
                val=None
            props[key]=val
        feature=geojson.Feature(geometry=pt,properties=props)
        return(feature)


    def getExtendedTablesByDatetime(self,date):
        """

        :synopsis: Get a list of extended tables for a given date.
        :param date: any date, e.g. "2017-01-01"
        :returns: list of extended table names (extended_*)

        Use this method to determine which extended tables
        to search for entries associated to an event.

        """

        year=None
        if isinstance(date,str):
          try:
            year=int(date[0:4])
          except ValueError:
            year=None

        elif isinstance(date,int):
            year=date
        elif hasattr(date,'year'):
            year=date.year

        if not year:
            raise ValueError('ERROR: getExtendedTablesByDatetime: Bad year in '+date)

        if year<self.EXT_MINYR:
            return self.exttables

        return self.exttables[(year-self.EXT_MINYR+1)::]


    def getPendingEvents(self,minResponses=1):
        """

        :synopsis: Get a list of events with minResponses.
        :param int minResponses: threshold of responses
        :returns: list of events, each row is an event

        Use this method to find events with pending responses.

        """

        table='event'
        clause='cast(newresponses as integer) >= ?'
        results=self.rawdb.query(table,clause,str(minResponses))
        if not results:
            return []
        return results

    def epochToString(epoch=None):
        # Turn epoch time into '2017-01-01 12:00:00'

        if epoch:
            dt=datetime.datetime.fromtimestamp(epoch,tz=datetime.timezone.utc)
        else:
            dt=datetime.datetime.utcnow()

        return dt.strftime('%Y-%m-%d %H:%M:%S')


    def incrementEvid(self,evid,checkAuth=False):
        """

        :synopsis: Increment newresponses for this evid
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns str results: see below

        """

        if self.evidIsUnknown(evid):
            return

        increment=1
        if checkAuth:
            raw=self.loadEvent(evid)
            if not raw:
                self.createStubEvent(evid)
                return

            if raw['newresponses']:
                increment+=raw['newresponses']

            if raw and raw['good_id']:
                evid=event['good_id']
 
        print('Db: Updating newresponses for',evid)
        self.rawdb.updateRow('event',evid,'newresponses',increment)
        return evid


        self.rawdb.update(table='event',key='eventid',value=updateId,column='newresponses',n=1,increment=True)
        return results.good_id


    def createStubEvent(self,evid,newresponses=1):

        print('Db: Creating stub event for',evid)
        stub={'eventid':evid,'newresponses':newresponses}
        results=self.rawdb.save('event',stub)
        return results


    def evidIsUnknown(self,evid):
        if not evid or evid=='unknown' or evid=='null':
            return True

            
