'''
Created on 09.05.2013

@author: dbub
'''

import PrivacyProxyAPI_pb2

class APIAction(object):
    '''
    This class implements the abstract base class for all API actions
    '''
    
    requiresAuthentication = False
    '''
    Indicate whether this APIACtion requires authentication
    '''
    
    command = None
    '''
    Which command does this action provide
    '''
    
    def __init__(self,dbConnection,userID=None,sessionID=None):
        '''
        Initialize this object instance
        '''
        self.dbConnection = dbConnection
        self.userID = userID
        self.sessionID = sessionID
    
    def process(self,data):
        '''
        Abstract processing method
        '''
        raise NotImplementedError(self.__class__, "This APIAction does not implement request processing")
    
    def _returnSuccess(self,data = None):
        '''
        Return a success result, containing the supplied data
        '''
        response = PrivacyProxyAPI_pb2.APIResponse()        
        response.command = self.command
        response.success = True
        response.errorCode = PrivacyProxyAPI_pb2.none
        
        # Set the data if it was supplied
        if data is not None:
            response.data = data.SerializeToString()
        
        return response
    
    def _returnError(self,errorCode):
        '''
        Return a error message. Set the error code
        '''
        response = PrivacyProxyAPI_pb2.APIResponse()
        response.command = self.command
        response.success = False
        response.errorCode = errorCode
        
        return response