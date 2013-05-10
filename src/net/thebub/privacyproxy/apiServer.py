'''
Created on 08.05.2013

@author: dbub
'''

from twisted.internet.protocol import Factory,Protocol
from twisted.internet import reactor
from twisted.python import log
from sys import stdout

import MySQLdb

from net.thebub.privacyproxy.actions.sessionActions import LoginAction,LogoutAction
import APICall_pb2

class APIServerProtocol(Protocol,object):
    
    apiActions = {
                  APICall_pb2.login : LoginAction,
                  APICall_pb2.logout : LogoutAction
    } 
    
    def __init__(self, factory):
        super(APIServerProtocol,self).__init__()
        self.factory = factory
        self.apiCall = APICall_pb2.APICall()
        self.dbCursor = factory.databaseConnection.cursor()

    def connectionMade(self):
        log.msg("Connection made!")

    def connectionLost(self, reason):
        log.msg("Connection lost!")
        
    def checkAuthentication(self,sessionKey):
        self.sessionKey = sessionKey
        return False
        
    def dataReceived(self, data):
        request = APICall_pb2.APICall()
        request.ParseFromString(data)
                
        response = None
        
        if request.command is not None and self.apiActions[request.command] is not None:
            action = self.apiActions[request.command](self)
            if not action.requiresAuthentication:
                response = self.transport.write(action.process(request.arguemnts))
            elif action.requiresAuthentication and request.sessionKey is not None and self.checkAuthentication(request.sessionKey):
                response = self.transport.write(action.process(request.arguemnts))
            else:
                log.msg("Request processing failed")
                
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
    databaseConnection = None
    
    def __init__(self,dbHost="localhost",dbUser="privacyproxy",dbPassword="privacyproxy",dbName="privacyproxy"):
        log.msg("Initializing API server")
        # Initialize the factory
        super(APIServerFactory,self).__init__()
                      
        # Open the database connection
        #self.databaseConnection = MySQLdb.connect(host=dbHost,user=dbUser,passwd=dbPassword,db=dbName)
        log.msg("Initialized API server successfully")
    
    def __del__(self):
        # When database connection exists, close it
        if self.databaseConnection is not None:
            self.databaseConnection.close()
    
    def buildProtocol(self, addr):
        # Create a APIProtocol instance
        return APIServerProtocol(self)
    
if __name__ == '__main__':
    log.startLogging(stdout)
    
    reactor.listenTCP(8081, APIServerFactory())
    reactor.run()
        