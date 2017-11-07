"""
rawDbSqlite
===========

.. note:: There are two versions of this module: :file:`rawDbSqlite.py` and :file:`rawDbMysql.py`. Change the header section of :file:`Db.py` to point to the correct implementation and make sure your :file:`db.json` file has the correct login information.


"""

import sqlite3

intcolumns=['nresponses','newresponses']
floatcolumns=['lat','lon','mag',
              'latitude','longitude',
              'lat_offset','lon_offset','lat_span','lon_span']

class RawDb:
    """

    :synopsis: Open a Sqlite connection.
    :param str dbparams: The name of a Config object (see config.py).

    Handles raw database transactions.

    """

    def __init__(self,dbparams):

        self.dbfiles=dbparams['files']
        self.cursors={}


    def getcursor(self,table):
        """

        :synopsis: Create a Sqlite3 cursor to a particular table.
        :param str table: A single table.
        :param str dbparams: The name of a Config object (see config.py).

        Handles raw database transactions.

        """


        if table in self.cursors:
            return self.cursors[table]

        if 'extended' in table:
            tablefile=self.dbfiles['extended']
            tablefile=tablefile.replace('__EXTENDED__',table)

        elif table in self.dbfiles:
            tablefile=self.dbfiles[table]

        else:
            raise NameError('getcursor could not find table '+table)

        print('RawDb: Connecting to file',tablefile)
        connector=sqlite3.connect(tablefile)
        connector.row_factory = sqlite3.Row
        cursor=connector.cursor()
        print('RawDb: Creating cursor for',table)
        self.cursors[table]=cursor

        return cursor


    def query(self,tables,clause,subs):
        """

        :synopsis: Query the database, splitting multiple tables if necessary
        :param tables: table or list of tables to query, see below
        :returns: list of rows returned by query

        The :py:attr:`tables` parameter accepts a single table, a comma-separated list of tables, or a list of tables. It calls :py:meth:`querySingleTable` on each table, then concatenates the results into a single list.

        """

        results=[]

        if isinstance(tables,str):
            tables=tables.split(',')

        for table in tables:
            tableresults=self.querySingleTable(table,clause,subs)
            if tableresults:
                results.extend(tableresults)

        return results


    def querySingleTable(self,table,clause,subs=None):
        """

        :synopsis: Query a single table of the database
        :param str table: table to be queried
        :returns: list of rows returned by query

        Note that no checking of table names is done at this step.

        """

        c=self.getcursor(table)
        query='SELECT * FROM '+table
        if clause:
            query+=' WHERE '+clause

        if isinstance(subs,str):
            subs=[subs]

        print('RawDb:',query)
        try:
            c.execute(query,subs)
        except sqlite3.OperationalError as e:
            raise NameError('sqlite3 Operational error: '+str(e))

        results=[]
        for row in c:
            # Sqlite data is a Row object, this is how you
            # turn it into a dict:
            rowdict=dict(zip(row.keys(),row))

            # Now convert certain columns to float or int
            for col,val in rowdict.items():
                if val is None:
                    continue
                if col in intcolumns:
                    rowdict[col]=int(val)
                elif col in floatcolumns:
                    rowdict[col]=float(val)

            # Now make a list
            rowdict['table']=table
            results.append(rowdict)

        if not results:
            return

        # results is now a list of dicts
        return results

