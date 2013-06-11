'''
Created on 11.05.2013

@author: dbub
'''

import MySQLdb

class DB(object):
    '''
    This class implements a wrapper for the MySQLdb class.
    It automatically handles reconncts and on-demand connection establishment.
    '''
    _connection = None
    _cursor = None
    
    _host = None
    _user = None
    _password = None
    _database = None

    def __init__(self,dbHost,dbUser,dbPassword,dbName):
        '''
        This constructor sets all necessary variables to connect to the database
        '''
        self._host = dbHost
        self._user = dbUser
        self._password = dbPassword
        self._database = dbName
        
    def __del__(self):
        '''
        When destroying the object, the database connection is closed
        '''
        self.diconnect()
        
    def _connect(self):
        '''
        Connect to the database using the provided credentials
        '''
        self._connection = MySQLdb.connect(host=self._host,user=self._user,passwd=self._password,db=self._database)
        
    def diconnect(self):
        '''
        Close the connection and reset all variables pointing to the old connection
        '''
        # Check whether a connection is present. Otherwise return immediately
        if self._connection is not None:
            # Check whether a cursor exists and destroy it, if necessary
            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None
            self._connection.close()
            self._connection = None
    
    def query(self,sql):
        '''
        Execute a query on the database and open the connection, of it was closed before
        '''
        try:
            # Check if a cursor exists. Otherwise create one
            if self._cursor is None:
                self._cursor = self._connection.cursor()
            self._cursor.execute(sql[0],sql[1])
        except (AttributeError, MySQLdb.OperationalError):
            # The connection was closed. Connect and reexecute the query.
            self._connect()
            self._cursor = self._connection.cursor()
            self._cursor.execute(sql[0],sql[1])
    
    def commit(self):
        '''
        Complete the transaction
        '''
        self._connection.commit()
        
    def insertid(self):
        '''
        Return the ID of the inserted row
        '''
        return self._cursor.lastrowid
            
    def rowcount(self):
        '''
        Get the count of rows returned by the previous query
        '''
        if self._cursor is not None:
            return self._cursor.rowcount
        else:
            return None
        
    def fetchone(self):
        '''
        Get the next row, returned by the previous query 
        '''
        if self._cursor is not None:
            return self._cursor.fetchone()
        else:
            return None
    
    def fetchall(self):
        '''
        Get all rows, returned by the previous query
        '''
        if self._cursor is not None:
            return self._cursor.fetchall()
        else:
            return None