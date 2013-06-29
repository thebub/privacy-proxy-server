'''
Created on 08.05.2013

@author: dbub
'''

from twisted.internet.protocol import Factory
from twisted.python import log

from net.thebub.privacyproxy.twisted.protobuf_delimited_protocol import ProtobufDelimitedProtocol
from net.thebub.privacyproxy.helpers.db import DB

from net.thebub.privacyproxy.apiserver.actions.sessionActions import LoginAction,LogoutAction
from net.thebub.privacyproxy.apiserver.actions.webLogActions import GetWebLogWebsitesAction,GetWebLogWebsiteDataAction
from net.thebub.privacyproxy.apiserver.actions.userActions import CreateUserAction,DeleteUserAction,UpdateUserAction
from net.thebub.privacyproxy.apiserver.actions.settingActions import GetSettingsAction,UpdateSettingAction


import PrivacyProxyAPI_pb2

class APIServerProtocol(ProtobufDelimitedProtocol):
    '''
    This class implements the ProtobufDelimited protocol and parses all requets to the API server
    '''
    
    apiActions = {
                  LoginAction.command : LoginAction,
                  LogoutAction.command : LogoutAction,
                  GetWebLogWebsitesAction.command : GetWebLogWebsitesAction,
                  GetWebLogWebsiteDataAction.command : GetWebLogWebsiteDataAction,
                  CreateUserAction.command : CreateUserAction,
                  DeleteUserAction.command : DeleteUserAction,
                  UpdateUserAction.command : UpdateUserAction,
                  GetSettingsAction.command : GetSettingsAction,
                  UpdateSettingAction.command : UpdateSettingAction
    }
    '''
    The supported API actions
    '''
    
    _message_class = PrivacyProxyAPI_pb2.APICall
    '''
    The request class which is parsed by the ProtobufDelimitedProtocol
    '''
    
    _sessionID = None
    _userID = None
    
    def __init__(self, factory, dbObject):
        '''
        Configure the ptocol and save the datbase connection
        '''        
        super(APIServerProtocol,self).__init__(factory)
                
        self._dbConnection = dbObject
        
    def _checkAuthentication(self,sessionID):
        '''
        Check the authentication of the user, using the supplied session ID
        '''
        self._dbConnection.query(("""SELECT user_id,session_id FROM session WHERE session_id = %s""",(sessionID,)))
        
        # If a row was returned the supplied session is valid
        if self._dbConnection.rowcount() == 1:
            result = self._dbConnection.fetchone()
             
            self._sessionID = sessionID
            self._userID = result[0]
                        
            return True        
        
        return False
        
    def messageReceived(self, request):
        '''
        Parse the received message and execute the desired API action
        '''                                
        response = None
        
        # Check whether the requested command is supported
        if request.command is not None and request.command in self.apiActions:
            # The command is supported. Check whether the command requires authentication
            if self.apiActions[request.command].requiresAuthentication and request.sessionKey is not None and not self._checkAuthentication(request.sessionKey):
                # The command requires authentication, but the user is not authenticated. Return an error message
                response = PrivacyProxyAPI_pb2.APIResponse()
                response.command = request.command
                response.success = False
                response.errorCode = PrivacyProxyAPI_pb2.unauthorized
            else:
                # No authentication was required or the user is authenticated. Process the request
                action = self.apiActions[request.command](self._dbConnection,self._userID,self._sessionID)           
                response = action.process(request.arguments)
        else:
            # The API command is not supported. Create a error response
            response = PrivacyProxyAPI_pb2.APIResponse()
            response.command = PrivacyProxyAPI_pb2.unknown
            response.success = False
            response.errorCode = PrivacyProxyAPI_pb2.badRequest
        
        # Send the response message to the client
        self.sendMessage(response)

class APIServerFactory(Factory,object):
    '''
    This class implements the protocol factory of the API server
    '''
    _host = None
    _user = None
    _password = None
    _database = None
    
    def __init__(self,dbHost,dbUser,dbPassword,dbName):
        '''
        Configure this protocol factory
        '''
        log.msg("Initializing API server")
        # Initialize the factory
        super(APIServerFactory,self).__init__()
        
        self._host = dbHost
        self._user = dbUser
        self._password = dbPassword
        self._database = dbName              
        
        log.msg("Initialized API server successfully")
    
    def buildProtocol(self,addr):
        '''
        Create a protocol instance and initialize a database connection for the instance
        '''      
        # Create DB object
        dbObject = DB(self._host, self._user, self._password, self._database)
        
        # Create and return a APIProtocol instance
        return APIServerProtocol(self, dbObject)
    