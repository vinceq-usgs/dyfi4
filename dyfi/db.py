# To use MySQL, switch the top line with this:
#import modules.rawDbMySQL as rawdb

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

    .. note:: To change to the database implementation to MySQL, see the heading of the :code:`db.py` module.

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

    EXT_MINYR=2015;
    EXT_MAXYR=2016;

    def __init__(self,config=None):

        self.rawdb=RawDb(config.db)
        self.params=config.db
        self.tables=['event','maps']
        self.exttables=['extended_'+str(x) for x in
            (['pre'] + list(range(self.EXT_MINYR,self.EXT_MAXYR+1)))]
        self.latesttable=self.exttables[-1]
        self.event=''

        self.tables.extend(self.exttables)


    def loadEvent(self,evid):
        """

        :synopsis: Read database for an event
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns: dict suitable for input to an :py:obj:`Event` instance

        This is mostly a wrapper to the `RawDb` :py:meth:`query` method.

        """

        table='event'
        clause='eventid=?'
        print('table:',table,'clause:',clause,'evid:',evid)
        results=self.rawdb.query(table,clause,evid)
        if not results:
            return

        if len(results)>1: # pragma: no cover
            warnings.warn(UserWarning('Multiple events found, using only the first'))

        results=results[0]
        return results


    def loadMaps(self,evid):
        """

        :synopsis: Get a list of maps for an event.
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

        The :attr:`table` parameter accepts a single table, a comma-separated list of tables, or a list of tables. Each table is either the table name, a year (for extended tables), or 'latest' or 'all' for extended tables.

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
                raise NameError('Db: no such table '+table)

        return outtables


    @classmethod
    def timeago(cls,t):
        t0=datetime.datetime.now()
        tdelta=datetime.timedelta(minutes=t)
        tnew=t0-tdelta
        return(tnew)


    @classmethod
    def row2geojson(cls,row):
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
            raise NameError('ERROR: getExtendedTablesByDatetime: Bad year in '+date)

        if year<self.EXT_MINYR:
            return self.exttables

        return self.exttables[(year-self.EXT_MINYR+1)::]


