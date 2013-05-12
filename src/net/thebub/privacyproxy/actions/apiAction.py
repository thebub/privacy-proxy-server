'''
Created on 09.05.2013

@author: dbub
'''
import hashlib, uuid, string

import APICall_pb2

class PasswordHelper(object):
    
    def _verifyPassword(self,password,hashedPassword,salt=None):
        return hashedPassword == self._hashPassword(password, salt)[0]            
    
    def _hashPassword(self,password,salt=None,createSalt=False):
        hashAlgorithm = hashlib.sha256()
                    
        if salt is None and createSalt:
            salt = uuid.uuid4().hex
        elif salt is None and not createSalt:
            self.protocol.dbConnection.query(("""SELECT user_salt FROM user WHERE id = %s """,(self.protocol.userID,)))
        
            if self.protocol.dbConnection.rowcount() == 1:
                result = self.protocol.dbConnection.fetchone()            
                salt = result[0]
            else:            
                raise ValueError("Could not obtain salt for current user.")
                
        saltedPassword = string.join([password,salt],"")
        
        hashAlgorithm.update(saltedPassword)
        passwordHash = hashAlgorithm.hexdigest()        
        
        return (passwordHash,salt)

class APIAction(object):
    requiresAuthentication = False
    command = None
    
    def __init__(self,protocol):
        self.protocol = protocol
        pass
    
    def process(self,data):
        raise NotImplementedError(self.__class__, "This APIAction does not implement request processing")
    
    def _returnSuccess(self,data = None):
        response = APICall_pb2.APIResponse()        
        response.command = self.command
        response.success = True
        response.errorCode = APICall_pb2.none
        
        if data is not None:
            response.data = data.SerializeToString()
        
        return response
    
    def _returnError(self,errorCode):
        response = APICall_pb2.APIResponse()
        response.command = self.command
        response.success = False
        response.errorCode = errorCode
        
        return response