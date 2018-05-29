"""

rawDbSqlite
===========

.. note:: The database currently implemented in SQLite 3. Low-level database operations are separated into this module in case we wish to reimplement to MySQL (or another solution) in the future.


"""

import sqlite3
import shutil
import os
import re

class RawDb:
    """

    :synopsis: Open a Sqlite connection.
    :param dbparams: A configuration `dict`, usually the 'db' section of a :py:obj:`dyfi.config.Config` object.

    Handles raw database transactions.

    .. data:: intcolumns

        A list of database columns that must be converted to type `int`.

    .. data:: floatcolumns

        A list of database columns that must be converted to type `float`.

    """

    intcolumns=['nresponses','newresponses']
    floatcolumns=['lat','lon','mag','depth',
        'latitude','longitude',
        'lat_offset','lon_offset','lat_span','lon_span']

    def __init__(self,dbparams):

        self.dbfiles=dbparams['files']
        self.cursors={}
        self.connectors={}
        self.columns={}

    def getCursor(self,table):
        """

        :synopsis: Create a Sqlite3 cursor to a particular table
        :param str table: Name of a single table

        This creates a Sqlite cursor, which is how Sqlite handles database transactions.

        """

        if table in self.cursors:
            return self.cursors[table]

        if 'extended' in table:
            tablefile=self.dbfiles['extended']
            tablefile=tablefile.replace('__EXTENDED__',table)

        elif table in self.dbfiles:
            tablefile=self.dbfiles[table]

        else:
            raise ValueError('getCursor could not find table '+table)

        if not os.path.isfile(tablefile):
            print('RawDb: Creating table',tablefile)
            self.createTable(tablefile,table=table)

        connector=sqlite3.connect(tablefile)
        connector.row_factory = sqlite3.Row

        # print('RawDb: New cursor for',table)
        cursor=connector.cursor()
        self.cursors[table]=cursor
        self.connectors[table]=connector

        return cursor


    def query(self,tables,clause,subs=None):
        """

        :synopsis: Query the database, splitting multiple tables if necessary
        :param tables: table or list of tables to query
        :returns: list of rows returned by query

        Calls :py:meth:`querySingleTable` on each table, then concatenates the results into a single list.

        The :py:attr:`tables` parameter accepts a single table or list of tables. No checking of table names is done at this step.

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

        No checking of table names is done at this step.
        Automagically fills in the 'table' key of each item.

        """

        if not self.validateTable(table):
            raise ValueError('Invalid table '+table)

        c=self.getCursor(table)
        query='SELECT * FROM %s' % table
        if clause:
            query+=' WHERE %s' % clause

        if subs and not isinstance(subs,list):
            subs=[subs]

        try:
            c.execute(query,subs) if subs else c.execute(query)

        except sqlite3.OperationalError as e:
            raise RuntimeError('sqlite3 Operational error: '+str(e))

        results=[]
        for row in c:

            # Sqlite data is a Row object, this is how you
            # turn it into a dict:
            rowdict=dict(zip(row.keys(),row))

            # Now convert certain columns to float or int
            for col,val in rowdict.items():
                if val is None:
                    continue
                if col in self.intcolumns:
                    rowdict[col]=int(val)
                elif col in self.floatcolumns:
                    rowdict[col]=float(val)

            # Now make a list
            rowdict['table']=table
            results.append(rowdict)

        if not results:
            return

        # results is now a list of dicts
        return results


    def updateRow(self,table,subid,column,val,increment=False):
        """

        :synopsis: Update a table row
        :param str table: table to be saved
        :param str subid: primary key value
        :param str column: column to be updated
        :param str val: new value
        :returns: number of rows changed

        This function is used to update a single row if the primary key is known (subid for extended tables, event ID for everything else.)

        """

        if not self.validateTable(table):
            raise ValueError('Invalid table '+table)

        c=self.getCursor(table)
        if 'extended' in table:
            primaryKey='subid'
        else:
            primaryKey='eventid'

        if increment:
            # incrementing does not work if original value is null
            # need to read the original column, then
            # increment manually

            clause='%s = ?' % primaryKey
            row=self.querySingleTable(table,clause,subid)[0]
            oldVal=row[column]
            if oldVal:
                val+=oldVal

        val=str(val)
        query='UPDATE %s SET %s=?' % (table,column)
        query+=' WHERE %s=?' % primaryKey
        try:
            c.execute(query,[val,subid])
            self.connectors[table].commit()

        except sqlite3.OperationalError as e:
            raise RuntimeError('sqlite3 Operational error: '+str(e))

        return c.rowcount


    def save(self,table,obj):
        """

        :synopsis: Save an object to the specified table
        :param str table: table to be saved
        :returns: primary key (subid of eventid)

        This saves an `Event` or `Entry` object to the database.

        """

        if not self.validateTable(table):
            raise ValueError('Invalid table '+table)

        c=self.getCursor(table)
        columns=self.getColumns(table)

        isDict=isinstance(obj,dict)

        saveList=[]
        for column in columns:
            if isDict and column in obj:
                val=obj[column]
            elif not isDict and hasattr(obj,column):
                val=getattr(obj,column)
            else:
                val=None

            saveList.append(val)

        query='INSERT OR REPLACE INTO '+table+' VALUES (%s)'
        query %=(','.join('?'*len(saveList)))

        try:
            c.execute(query,saveList)
            self.connectors[table].commit()

        except (sqlite3.OperationalError,sqlite3.IntegrityError) as e:
            raise RuntimeError('sqlite3 Operational error: '+str(e))

        if 'extended' in table:
            return c.lastrowid
        else:
            return obj['eventid'] if isDict else obj.eventid


    def getColumns(self,table):
        """

        :synopsis: Read columns from a database table
        :param str table: A database table to read
        :returns: List of columns

        This is used to get the list of columns in table, so that the save function can save a row properly.

        This will also populate the `columns` attribute.

        """

        if not self.validateTable(table):
            raise ValueError('Invalid table '+table)

        if table in self.columns:
            return self.columns[table]

        # Cursor is saved, this won't open a duplicate cursor
        c=self.getCursor(table)
        c.execute('SELECT * FROM %s' % table)
        columns=[tuple[0] for tuple in c.description]
        self.columns[table]=columns

        return columns


    def createTable(self,tablefile,table=None):
        """

        :synopsis: Create a database table from a template
        :param str tablefile: The name of the table file

        This creates a new table from a table template (the DYFI tables are implemented in Sqlite, one .sql file per table.) The template is a blank table file with the extension '.template' in the same directory as the other Sqlite tables.

        """

        if table and not self.validateTable(table):
            raise ValueError('Invalid table '+table)

        templatefile=tablefile+'.template'
        if 'extended' in tablefile:
            # The template for all extended_* databases is
            # .../extended.db.template
            templatefile=self.dbfiles['extended']+'.template'
            templatefile=templatefile.replace('__EXTENDED__','extended')

        print('RawDb.createTable: creating',tablefile,'from',templatefile)
        shutil.copy(templatefile,tablefile)

        if 'extended' in table:
            connector=sqlite3.connect(tablefile)
            connector.row_factory = sqlite3.Row
            c=connector.cursor()
            c.execute('ALTER TABLE extended RENAME TO '+table)
            connector.commit()

    @staticmethod
    def validateTable(table):

        if table=='event':
            return True
        if table=='extended_pre':
            return True
        if re.search('^extended_\d{4}$',table):
            return True

        return False

