'''
Created on 11.05.2013

@author: dbub
'''

import MySQLdb

class DB(object):
    _connection = None
    _cursor = None
    
    _host = None
    _user = None
    _password = None
    _database = None

    def __init__(self,dbHost,dbUser,dbPassword,dbName):
        self._host = dbHost
        self._user = dbUser
        self._password = dbPassword
        self._database = dbName
        
    def __del__(self):
        if self._cursor is not None:
            self._cursor.close()
        self._connection.close()
    
    def _connect(self):
        self._connection = MySQLdb.connect(host=self._host,user=self._user,passwd=self._password,db=self._database)
    
    def query(self,sql):
        try:
            if self._cursor is None:
                self._cursor = self._connection.cursor()
            self._cursor.execute(sql[0],sql[1])
        except (AttributeError, MySQLdb.OperationalError):
            self._connect()
            self._cursor = self._connection.cursor()
            self._cursor.execute(sql[0],sql[1])
    
    def commit(self):
        self._connection.commit()
            
    def rowcount(self):
        if self._cursor is not None:
            return self._cursor.rowcount
        else:
            return None
        
    def fetchone(self):
        if self._cursor is not None:
            return self._cursor.fetchone()
        else:
            return None
    