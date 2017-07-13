"""
rawdb
=====

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
    
    """
    def __init__(self,dbparams):
        
        self.dbfiles=dbparams['files']
        self.cursors={}

        
    def getcursor(self,table):
        
        if table in self.cursors:
            return self.cursors[table]
        
        if 'extended' in table:
            tablefile=self.dbfiles['extended']
            tablefile=tablefile.replace('__EXTENDED__',table)

        elif table in self.dbfiles:
            tablefile=self.dbfiles[table]

        else:
            raise NameError('getcursor could not find table '+table)

            
        print('Connecting to file',tablefile)
        connector=sqlite3.connect(tablefile)
        connector.row_factory = sqlite3.Row
        cursor=connector.cursor()
        print('Creating cursor for',table)
        self.cursors[table]=cursor
        
        return cursor
        
        
    def query(self,tables,clause):

        results=[]

        if ',' in tables:
            raise nameError('Cannot handle string')

        if isinstance(tables,str):
            tables=[tables]
            
        for table in tables:
            tableresults=self.querySingleTable(table,clause)
            if tableresults:
                results.extend(tableresults)
            
        print('DEBUG: rawDbSqlite.query got',len(results),'results')
        return results
        
        
    def querySingleTable(self,table,clause):

        c=self.getcursor(table)
        query='SELECT * FROM '+table
        if clause:
            query+=' WHERE '+clause

        print(query)
        c.execute(query)

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
        

    def getExtendedTablesByTable(self,table):
        # Handle 'latest', 'all', or year
        
        if table=='all':
            return self.exttables
        
        if table.isdigit():
            newtable='extended_'+table
            if newtable in self.exttables:
                return newtable
            else:
                raise NameError('db.getExtendedTablesByTable got bad table',newtable)

        if table=='pre':
            return 'extended_pre'
 
        
    def update(self,table,query,changes):
        
        c=self.getcursor(table)
        query='UPDATE %s SET %s WHERE %s' % (table,setstring,clause)
        c.execute(query)
        
        return c.rowcount
