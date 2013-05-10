'''
Created on 08.05.2013

@author: dbub
'''

from twisted.internet.protocol import Factory,Protocol
from twisted.protocols.basic import LineReceiver

from twisted.internet import reactor

from twisted.python import log
import sys

from net.thebub.privacyproxy.actions.sessionActions import LoginAction,LogoutAction

import MySQLdb

import APICall_pb2

class APIServerProtocol(Protocol):
    
    apiActions = {
                  APICall_pb2.login : LoginAction,
                  APICall_pb2.logout : LogoutAction
    } 
    
    def __init__(self, factory):
        self.factory = factory
        self.apiCall = APICall_pb2.APICall()

    def connectionMade(self):
        log.msg("Connection made!")

    def connectionLost(self, reason):
        log.msg("Connection lost!")
        
    def checkAuthentication(self,sessionKey):
        return False
        
    def dataReceived(self, data):
        log.msg("API Call received")
        request = APICall_pb2.APICall()
        request.ParseFromString(data)
        log.msg("API Call decoded")
        
        if request.command is not None and self.apiActions[request.command] is not None:
            action = self.apiActions[request.command]()
            if not action.requiresAuthentication:
                self.transport.write(action.process(request.arguemnts))
            elif action.requiresAuthentication and request.sessionKey is not None and self.checkAuthentication(request.sessionKey):
                self.transport.write(action.process(request.arguemnts))
            else:
                log.msg("Request processing failed")
                
                response = APICall_pb2.APIResponse()
                response.command = request.command
                response.success = False
                
                self.transport.write(response.SerializeToString())
                
        log.msg("API Call processing completed")

class APIServerFactory(Factory):
    
    databaseConnection = None
    
    def __init__(self,dbHost="localhost",dbUser="privacyproxy",dbPassword="privacyproxy",dbName="privacyproxy"):
        log.msg("Initializing API server")
        # Initialize the factory
        #super(Factory,self)
                      
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
    log.startLogging(sys.stdout)
    
    reactor.listenTCP(8081, APIServerFactory())
    reactor.run()
        