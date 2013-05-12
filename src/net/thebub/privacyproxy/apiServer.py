'''
Created on 08.05.2013

@author: dbub
'''

from twisted.internet.protocol import Factory,Protocol
from twisted.internet import reactor
from twisted.python import log
from sys import stdout

from net.thebub.privacyproxy.actions.sessionActions import LoginAction,LogoutAction
from net.thebub.privacyproxy.actions.webLogActions import GetWebLogWebsitesAction,GetWebLogWebsiteDataAction
from net.thebub.privacyproxy.actions.userActions import CreateUserAction,DeleteUserAction,UpdateUserAction
from net.thebub.privacyproxy.db import DB

import APICall_pb2

class APIServerProtocol(Protocol,object):
    
    apiActions = {
                  LoginAction.command : LoginAction,
                  LogoutAction.command : LogoutAction,
                  GetWebLogWebsitesAction.command : GetWebLogWebsitesAction,
                  GetWebLogWebsiteDataAction.command : GetWebLogWebsiteDataAction,
                  CreateUserAction.command : CreateUserAction,
                  DeleteUserAction.command : DeleteUserAction,
                  UpdateUserAction.command : UpdateUserAction 
    } 
    
    def __init__(self, factory, dbObject):
        super(APIServerProtocol,self).__init__()
        self.factory = factory               
        self.dbConnection = dbObject
        
        self.apiCall = APICall_pb2.APICall()

    def __del__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass
        
    def checkAuthentication(self,sessionID):
        self.dbConnection.query(("""SELECT user_id,session_id FROM session WHERE session_id = %s""",(sessionID,)))
                
        if self.dbConnection.rowcount() == 1:
            result = self.dbConnection.fetchone()
             
            self.sessionID = sessionID
            self.userID = result[0]
                        
            return True        
        
        return False
        
    def dataReceived(self, data):
        request = APICall_pb2.APICall()
        request.ParseFromString(data)
                
        response = None
        
        if request.command is not None and self.apiActions[request.command] is not None:
            action = self.apiActions[request.command](self)
            if not action.requiresAuthentication:
                response = action.process(request.arguments)
            elif action.requiresAuthentication and request.sessionKey is not None and self.checkAuthentication(request.sessionKey):
                response = action.process(request.arguments)
            else:                
                response = APICall_pb2.APIResponse()
                response.command = request.command
                response.success = False
                response.errorCode = APICall_pb2.unauthorized
        else:
            response = APICall_pb2.APIResponse()
            response.command = APICall_pb2.unknown
            response.success = False
            response.errorCode = APICall_pb2.badRequest
             
        self.transport.write(response.SerializeToString())

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
    
    def buildProtocol(self, addr):
        
        # Create DB object
        dbObject = DB(self._host, self._user, self._password, self._database)
        
        # Create and return a APIProtocol instance
        return APIServerProtocol(self, dbObject)
    
if __name__ == '__main__':
    log.startLogging(stdout)
    
    reactor.listenTCP(8081, APIServerFactory("thebub.net","privacyproxy","seemoo!delphine"))
    reactor.run()
        