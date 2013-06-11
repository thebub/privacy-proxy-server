'''
Created on 13.05.2013

@author: dbub
'''

import hashlib, uuid, string

class PasswordHelper(object):
    '''
    This helper class implements functions, which handle password hashing.
    '''
    
    def __init__(self,dbConnection,userID=None):
        '''
        Configure this instance of the helper
        ''' 
        self.dbConnection = dbConnection
        self.userID = userID
    
    def _verifyPassword(self,password,hashedPassword,salt=None):
        '''
        Return a boolean value, indicating the correctness of the password
        '''
        return hashedPassword == self._hashPassword(password, salt)[0]            
    
    def _hashPassword(self,password,salt=None,createSalt=False):
        '''
        This function returns the hashed password.
        If no salt exists, this function will generate a salt automatically
        '''
        hashAlgorithm = hashlib.sha256()
        
        # Check whether a salt should be generated
        if salt is None and createSalt:
            salt = uuid.uuid4().hex
        elif salt is None and not createSalt:
            self.dbConnection.query(("""SELECT password_salt FROM user WHERE id = %s """,(self.userID,)))
        
            if self.dbConnection.rowcount() == 1:
                result = self.dbConnection.fetchone()            
                salt = result[0]
            else:            
                raise ValueError("Could not obtain salt for current user.")
        
        # Concatenate the password and salt
        saltedPassword = string.join([password,salt],"")
        
        # Create the hash of the salted password
        hashAlgorithm.update(saltedPassword)
        passwordHash = hashAlgorithm.hexdigest()        
        
        # Return the touple of password and used salt
        return (passwordHash,salt)