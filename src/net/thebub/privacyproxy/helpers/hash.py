'''
Created on 13.05.2013

@author: dbub
'''

import hashlib, uuid, string

class DataHashHelper(object):
    '''
    This class implements utility functions to handle salted hashing of private data 
    '''
    
    def __init__(self,dbConnection,userID):
        '''
        Configure this helper class
        '''
        self.dbConnection = dbConnection
        self.userID = userID
    
    def _createDataSalt(self):
        '''
        Create a salt for data hashing
        '''
        return uuid.uuid4().hex
    
    def _getSalt(self):
        '''
        Get the salt for the current user of the database.
        '''
        self.dbConnection.query(("""SELECT data_salt FROM user WHERE id = %s """,(self.userID,)))
        
        if self.dbConnection.rowcount() == 1:
            return self.dbConnection.fetchone()[0]
        
        raise ValueError("Could not obtain data salt for user.")
    
    def _hashData(self,data):
        '''
        Return the salted hash of the provided data
        '''
        hashAlgorithm = hashlib.sha256()
        
        # Concatenate the data and the salt
        saltedData = string.join([data,self._getSalt()],"")
        
        # Get the hex digest of the salt concatenated data
        hashAlgorithm.update(saltedData)
        hashedData = hashAlgorithm.hexdigest()        
        
        return hashedData