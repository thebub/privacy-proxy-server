'''
Created on 13.05.2013

@author: dbub
'''

import hashlib, uuid, string

class DataHashHelper(object):
    
    def __init__(self,dbConnection,userID):
        self.dbConnection = dbConnection
        self.userID = userID
    
    def _createDataSalt(self):
        return uuid.uuid4().hex
    
    def _getSalt(self):
        self.dbConnection.query(("""SELECT data_salt FROM user WHERE id = %s """,(self.userID,)))
        
        if self.dbConnection.rowcount() == 1:
            return self.dbConnection.fetchone()[0]
        
        raise ValueError("Could not obtain data salt for user.")
    
    def _hashData(self,data):
        hashAlgorithm = hashlib.sha256()
        
        saltedData = string.join([data,self._getSalt()],"")
        
        hashAlgorithm.update(saltedData)
        hashedData = hashAlgorithm.hexdigest()        
        
        return hashedData