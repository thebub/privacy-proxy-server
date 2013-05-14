'''
Created on 08.05.2013

@author: dbub
'''

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.python import log
from sys import stdout

from net.thebub.privacyproxy.twisted.protobuf_delimited_protocol import ProtobufDelimitedProtocol
from net.thebub.privacyproxy.helpers.db import DB

from net.thebub.privacyproxy.apiserver.actions.sessionActions import LoginAction,LogoutAction
from net.thebub.privacyproxy.apiserver.actions.webLogActions import GetWebLogWebsitesAction,GetWebLogWebsiteDataAction
from net.thebub.privacyproxy.apiserver.actions.userActions import CreateUserAction,DeleteUserAction,UpdateUserAction
from net.thebub.privacyproxy.apiserver.actions.settingActions import GetSettingsAction,UpdateSettingAction


import PrivacyProxyAPI_pb2

class APIServerProtocol(ProtobufDelimitedProtocol):
    
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
    
    _message_class = PrivacyProxyAPI_pb2.APICall
    
    _sessionID = None
    _userID = None
    
    def __init__(self, factory, dbObject):        
        super(APIServerProtocol,self).__init__(factory)
                
        self._dbConnection = dbObject
        
    def _checkAuthentication(self,sessionID):
        self._dbConnection.query(("""SELECT user_id,session_id FROM session WHERE session_id = %s""",(sessionID,)))
                
        if self._dbConnection.rowcount() == 1:
            result = self._dbConnection.fetchone()
             
            self._sessionID = sessionID
            self._userID = result[0]
                        
            return True        
        
        return False
        
    def messageReceived(self, request):                                
        response = None
        
        if request.command is not None and self.apiActions[request.command] is not None:
            if self.apiActions[request.command].requiresAuthentication and request.sessionKey is not None and not self._checkAuthentication(request.sessionKey):
                response = PrivacyProxyAPI_pb2.APIResponse()
                response.command = request.command
                response.success = False
                response.errorCode = PrivacyProxyAPI_pb2.unauthorized
            else:                                
                action = self.apiActions[request.command](self._dbConnection,self._userID,self._sessionID)           
                response = action.process(request.arguments)
        else:
            response = PrivacyProxyAPI_pb2.APIResponse()
            response.command = PrivacyProxyAPI_pb2.unknown
            response.success = False
            response.errorCode = PrivacyProxyAPI_pb2.badRequest
        
        self.sendMessage(response)

class APIServerFactory(Factory,object):
    _host = None
    _user = None
    _password = None
    _database = None
    
    def __init__(self,dbHost="localhost",dbUser="privacyproxy",dbPassword="privacyproxy",dbName="privacyproxy"):
        log.msg("Initializing API server")
        # Initialize the factory
        super(APIServerFactory,self).__init__()
        
        self._host = dbHost
        self._user = dbUser
        self._password = dbPassword
        self._database = dbName              
        
        log.msg("Initialized API server successfully")
    
    def __del__(self):
        # When database connection exists, close it
        if self.databaseConnection is not None:
            self.databaseConnection.close()
    
    def buildProtocol(self,addr):        
        # Create DB object
        dbObject = DB(self._host, self._user, self._password, self._database)
        
        # Create and return a APIProtocol instance
        return APIServerProtocol(self, dbObject)
    
if __name__ == '__main__':
    log.startLogging(stdout)
    
    reactor.listenTCP(8081, APIServerFactory("thebub.net","privacyproxy","seemoo!delphine"))
    reactor.run()
        