'''
Created on 13.05.2013

@author: dbub
'''

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import sys, hashlib, string, threading

from net.thebub.privacyproxy.twisted.authProxyRequest import AuthProxyRequest
from net.thebub.privacyproxy.helpers.db import DB
from net.thebub.privacyproxy.proxyserver.analysisThread import analysisQueue,AnalysisThread

class PrivacyProxyRequest(AuthProxyRequest,object):
    _realmName = "PrivacyProxy"
    _userID = None
    
    _dbHost = "thebub.net"
    _dbUser = "privacyproxy"
    _dbPassword = "seemoo!delphine"
    _dbDatabase = "privacyproxy"
    
    def requiresUserAuth(self):
        return True
            
    def checkUserAuth(self, username, password):
        hashAlgorithm = hashlib.sha256()
        self.dbConnection = DB(self._dbHost, self._dbUser, self._dbPassword, self._dbDatabase)
        
        self.dbConnection.query(("""SELECT password_salt FROM user WHERE username = %s;""",(username,)))
        
        if self.dbConnection.rowcount() == 1:
            salt = self.dbConnection.fetchone()[0]
            saltedPassword = string.join([password,salt],"")
        
            hashAlgorithm.update(saltedPassword)
            passwordHash = hashAlgorithm.hexdigest()
            
            self.dbConnection.query(("""SELECT id FROM user WHERE username = %s AND password = %s;""",(username,passwordHash)))
            
            if self.dbConnection.rowcount() == 1:
                self._userID = self.dbConnection.fetchone()[0]                
                return True
            
        return False
    
    def proxyRequestReceived(self):
        
        analysisData = {}
        analysisData['userID'] = self._userID
        analysisData['post'] = "POST"
        analysisData['get'] = "GET"
        analysisData['ajax'] = "AJAX"
                
        analysisQueue.put(analysisData)
        
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print "HTTPS is not supported at the moment!"

class PrivacyProxy(proxy.Proxy):
    requestFactory = PrivacyProxyRequest

class PrivacyProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return PrivacyProxy()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    
    t = AnalysisThread()
    t.start()
    
    reactor.listenTCP(8080, PrivacyProxyFactory())
    reactor.run()