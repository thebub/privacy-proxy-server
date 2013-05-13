'''
Created on 13.05.2013

@author: dbub
'''

import hashlib, uuid, string

class PasswordHelper(object):
    
    def __init__(self,dbConnection,userID=None):
        self.dbConnection = dbConnection
        self.userID = userID
    
    def _verifyPassword(self,password,hashedPassword,salt=None):
        return hashedPassword == self._hashPassword(password, salt)[0]            
    
    def _hashPassword(self,password,salt=None,createSalt=False):
        hashAlgorithm = hashlib.sha256()
                    
        if salt is None and createSalt:
            salt = uuid.uuid4().hex
        elif salt is None and not createSalt:
            self.dbConnection.query(("""SELECT password_salt FROM user WHERE id = %s """,(self.userID,)))
        
            if self.dbConnection.rowcount() == 1:
                result = self.dbConnection.fetchone()            
                salt = result[0]
            else:            
                raise ValueError("Could not obtain salt for current user.")
                
        saltedPassword = string.join([password,salt],"")
        
        hashAlgorithm.update(saltedPassword)
        passwordHash = hashAlgorithm.hexdigest()        
        
        return (passwordHash,salt)