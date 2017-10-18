"""

Db
==

"""

import warnings
from .rawDbSqlite import RawDb

# To use MySQL, switch the top line with this:
#import modules.rawDbMySQL as rawdb

import geojson
import datetime

class Db:
    """

    :synopsis: Open a connection to access the DYFI database.
    :param config: Optional Config object

    This connection is required to run any database queries.
    The database is currently implemented in SQLite.

    .. data:: exttables

        A list of all the extended tables.

    .. data:: latesttable

        The name of the latest extended table
        (should be the current year, e.g. "extended_2016").

    .. note:: To change to the database implementation to MySQL,
    see the heading of the :code:`db.py` module.

    """

    # TODO: generalize this for all available years
    EXT_MINYR=2015;
    EXT_MAXYR=2016;

    def __init__(self,config=None):

        self.rawdb=RawDb(config.db)
        self.params=config.db
        self.exttables=['extended_'+str(x) for x in
            (['pre'] + list(range(self.EXT_MINYR,self.EXT_MAXYR+1)))]
        self.latesttable=self.exttables[-1]
        self.event=''


    def loadEvent(self,evid):
        """

        :synopsis: Get data for an event.
        :param str evid: event ID, e.g. 'us1000abcd'
        :returns: dict suitable for input to an :py:obj:`Event` instance

        This is mostly a wrapper to :py:obj:`query`.

        """

        table='event'
        clause="eventid='"+str(evid)+"'"
        results=self.rawdb.query(table,clause)
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

        This is mostly a wrapper to :py:obj:`query`.

        Each item in the return list is a dict with keys
        being columns to the maps table.

        """

        table='maps'
        clause="eventid='"+str(evid)+"'"
        results=self.rawdb.query(table,clause)
        if not results:
            return

        # We expect multiple rows
        return results


    def loadEntries(self,evid=None,event=None,
                    table=None,startdatetime=None,
                    querytext=None):
        """

        :synopsis: Search the extended tables for entries matching a query.
        :param str evid: optional eventid
        :param Event event: optional Event object
        :param table: optional table or comma-delimited table or list of tables
        :param startdatetime: optional datetime to start search
        :param str querytext: optional clause(s)
        :returns: list of entries suitable for aggregation

        This is mostly a wrapper to :py:obj:`query`. It also
        figures out which extended tables to search,
        depending on the date of the event, using
        :py:obj:`getExtendedTablesByDatetime`.

        The optional query parameter is a string of SQL `WHERE` clauses
        (e.g. 'suspect=0 OR suspect is null').

        Each item in the return list is a dict of entries from the extended tables, plus an additional key `table` that contains the name of the source extended table (see :py:obj:`query`).
        """

        # First, figure out which tables to check

        if table:
          if table=='latest':
            table=self.latesttable
          elif table=='all':
            table=self.exttables
          elif 'extended_'+table in self.exttables:
            table='extended_'+table

        elif not table:
            if startdatetime:
                table=self.getExtendedTablesByDatetime(startdatetime)
            elif event:
                table=self.getExtendedTablesByDatetime(event.eventdatetime)
            else:
                print('Db: WARNING: db.loadEntries using latest table only')
                table=self.latesttable

        # Second, figure out which eventid to query

        myclauses=[]

        if querytext:
            myclauses.append(querytext)

        if event and not evid:
            evid=event.eventid

        if evid:
            myclauses.append('eventid="%s"' % (evid))

        if startdatetime:
            myclauses.append('time_now>="%s"' % (startdatetime))

        # Finally, combine queries

        if myclauses:
            querytext=' AND '.join(myclauses)

        results=self.rawdb.query(table,querytext)
        return results


    def rawStatement(self,text):
        """

        :synopsis: Simplest SQL query with the raw query string, no formatting.

        :param str text: SQL query string
        :returns: list

        Use this in case an application needs to do low-level SQL operations.

        The return value is a list of table rows, where each row is a dict.

        """

        self.statement=text
        print('Db: rawStatement:',text)
        return self.rawdb.execute(text)

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
        :param date: any date
        :param type: datetime or str or int
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


# End of function defs

# Not tested yet
if __name__=='__main__': # pragma: no cover
    import argparse
    parser=argparse.ArgumentParser(
        description='Access the DYFI database.'
    )
    parser.add_argument('query',type=str,nargs='?',
        help="SQL query (raw query, if no --extended)")
    parser.add_argument('--dbfile',type=str,nargs='?',default=None,
        help="db.json file with database settings")
    parser.add_argument('--extended',type=str,nargs='?',
        help="Extended query with geojson output. Add a comma-separated list of columns as output or leave blank for all columns.")
    args=parser.parse_args()
    print('Db: opening with',args.dbfile)

    db=Db(args.dbfile)
    if args.extended:
        if not args.query:
            args.query=args.extended
            args.extended=True

        table='all'
        if isinstance(args.extended,str):
            table=args.extended
        results=db.extquery('*',table,args.query)
        for row in results:
            print(row.properties['table'],':',str(row.properties['subid']))
        exit()

    else:
        results=db.rawStatement(args.query)

    print(results)

