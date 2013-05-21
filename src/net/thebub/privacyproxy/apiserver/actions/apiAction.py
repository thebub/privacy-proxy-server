'''
Created on 09.05.2013

@author: dbub
'''

import PrivacyProxyAPI_pb2

class APIAction(object):
    requiresAuthentication = False
    command = None
    
    def __init__(self,dbConnection,userID=None,sessionID=None):
        self.dbConnection = dbConnection
        self.userID = userID
        self.sessionID = sessionID
        pass
    
    def process(self,data):
        raise NotImplementedError(self.__class__, "This APIAction does not implement request processing")
    
    def _returnSuccess(self,data = None):
        response = PrivacyProxyAPI_pb2.APIResponse()        
        response.command = self.command
        response.success = True
        response.errorCode = PrivacyProxyAPI_pb2.none
        
        if data is not None:
            response.data = data.SerializeToString()
        
        return response
    
    def _returnError(self,errorCode):
        response = PrivacyProxyAPI_pb2.APIResponse()
        response.command = self.command
        response.success = False
        response.errorCode = errorCode
        
        return response