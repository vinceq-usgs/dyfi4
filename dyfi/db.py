# To use MySQL,
# 1. change import from .rawDbSqlite to .rawDbMysql
# 2. same for dyfi/__init__.py

import warnings
from .rawDbSqlite import RawDb

import geojson
import datetime

class Db:
    """

    :synopsis: Open a connection to access the DYFI database
    :param config: (optional) :py:class:`Config` object

    This connection is required to run all database queries.
    The database is currently implemented in SQLite.

    .. note:: To change to the database implementation to MySQL, see the top of this file.

    .. data:: TABLES

        A list of all tables (including extended tables).

    .. data:: EXTTABLES

        A list of all the extended tables.

    .. data:: EXT_MINYR

       The year of the earliest named extended table. Previous entries are combined into the table 'extended_pre'.

    .. data:: EXT_MAXYR

       The year of the latest defined extended table. This is calculated from the current year.

    .. attribute:: latesttable

        The name of the latest extended table.

     """

    # TODO:
    # create latest table with up to two years of latest entries
    # automatically calculate tables: ...2014,2015,extended

    EXT_MINYR=2003;
    EXT_MAXYR=datetime.datetime.utcnow().year
    TABLES=['event','maps']
    EXTTABLES=['extended_'+str(x) for x in
            (['pre'] + list(range(EXT_MINYR,EXT_MAXYR+1)))]
    TABLES.extend(EXTTABLES)


    def __init__(self,config=None):

        self.rawdb=RawDb(config.db) if config else None
        self.params=config.db
        self.latesttable=Db.EXTTABLES[-1]
        self.event=''


    def save(self,obj,table=None):
        """

        :synopsis: Save a :py:class:`dyfi.Event` or :py:class:`dyfi.Entry` object to the database table
        :param obj: Data object
        :returns: Success or failure

        Save this object to the database. This is mostly a stub to the `RawDb` :py:obj:`save` function.

        If the primary exists on this table (eventid or subid), this will rewrite the row. Otherwise, it will create a new row.

        For consistency, if the object is an `Entry` object, this will automagically overwrite the `table` attribute.

        """

        isDict=isinstance(obj,dict)
        if not table: 
            if hasattr(obj,'table'):
                table=obj.table
            elif isDict:
                table=obj['table']

        if not table:
            raise ValueError('Db.save: table not specified')

        if table=='extended':
            time_now=obj['time_now'] if isDict else obj.time_now
            table=self.getExtendedTablesByDatetime(time_now)[0]

        if table=='event' or 'extended' in table:
            if isDict:
                obj['table']=table
            else:
                obj.table=table
            return self.rawdb.save(table,obj)

        raise RuntimeError('Db.save: unsupported table')


    def loadEvent(self,evid):
        """

        :synopsis: Read database for event data for an event ID
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns: `dict` suitable for input to an :py:obj:`Event` instance

        This is mostly a wrapper to the `RawDb` :py:meth:`query` method. This returns a `dict` with keys being columns of the `Event` table.

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


    def loadEntries(self,evid=None,event=None,
                    table=None,startdatetime=None,
                    querytext=None,loadSuspect=False):
        """

        :synopsis: Search the extended tables for entries matching a query
        :param str evid: (optional) eventid
        :param Event event: (optional) Event object
        :param table: (optional) table or tables
        :param startdatetime: (optional) datetime to start search
        :param str querytext: (optional) clause(s)
        :returns: list of entries suitable for aggregation

        This is mostly a wrapper to the :py:obj:`rawDBSqlite` :py:obj:`query` object.

        It also figures out which extended tables to search,
        depending on the date of the event, using
        :py:obj:`getExtendedTablesByDatetime`.

        For valid values of parameter :py:attr:`table` see the :py:meth:`checkTables` method.

        The optional query parameter is a string of SQL `WHERE` clauses
        (e.g. 'suspect=0 OR suspect is null').

        Each item in the return list is a `dict` of entries from the `extended` tables. An additional key `table` is added to each entry that contains the name of the source extended table (see :py:obj:`query`).

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

        if not loadSuspect:
            myclauses.append('(suspect="" or suspect=0 or suspect is null)')

        # Finally, combine queries

        if myclauses:
            querytext=' AND '.join(myclauses)

        # This will automagically create a 'table' key for each entry
        results=self.rawdb.query(table,querytext,mysubs)
        return results


    def checkTables(self,table):
        """

        :synopsis: Check that the table or tables exist
        :param table: Table or list of tables, see below
        :returns: list of matching table names

        The :attr:`table` parameter accepts one or more extended tables (comma-seperated string or list). Each table is either the table name, a year, or 'latest' or 'all' for extended tables.

        The return value is a list of proper table names ('2016' will be converted to 'extended_2016', etc.) If any of the tables don't exist, a ValueError is returned.

        """

        if table=='all':
            return Db.EXTTABLES

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

            if table in Db.TABLES:
                outtables.append(table)

            elif 'extended_'+table in Db.TABLES:
                outtables.append('extended_'+table)

            else:
                raise ValueError('Db: no such table '+table)

        return outtables


    @classmethod
    def row2geojson(cls,row):
        """

        :synopsis: Convert a raw dictionary into a GeoJSON object
        :param dict row: A `dict`, such as extracted from an `extended` table
        :returns: :py:obj:`GeoJSON` object

        This returns a `GeoJSON` object by extracting the latitude and longitude.

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

    @classmethod
    def getExtendedTablesByDatetime(cls,date):
        """

        :synopsis: Get a list of extended tables for a given date
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

        if year<Db.EXT_MINYR:
            return Db.EXTTABLES

        return Db.EXTTABLES[(year-Db.EXT_MINYR+1)::]


    @staticmethod
    def timeago(t):
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


    @staticmethod
    def epochToString(epoch=None):
        # Turn epoch time into '2017-01-01 12:00:00'

        if epoch:
            dt=datetime.datetime.fromtimestamp(epoch,tz=datetime.timezone.utc)
        else:
            dt=datetime.datetime.utcnow()

        return dt.strftime('%Y-%m-%d %H:%M:%S')



