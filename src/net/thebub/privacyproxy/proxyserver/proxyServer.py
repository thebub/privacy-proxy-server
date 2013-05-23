'''
Created on 13.05.2013

@author: dbub
'''

from twisted.web import proxy, http
from twisted.python import log
import hashlib, string, re

from net.thebub.privacyproxy.twisted.authProxyRequest import AuthProxyRequest
from net.thebub.privacyproxy.helpers.db import DB
from net.thebub.privacyproxy.proxyserver.analysisThread import analysisQueue,AnalysisThread

class PrivacyProxyRequest(AuthProxyRequest,object):
    _realmName = "PrivacyProxy"
    _userID = None
        
    def requiresUserAuth(self):
        return True
            
    def checkUserAuth(self, username, password):
        hashAlgorithm = hashlib.sha256()
        self.dbConnection = DB(self.channel._dbHost, self.channel._dbUser, self.channel._dbPassword, self.channel._dbDatabase)
        
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
    
    def analyzeURL(self):
        url = self.path
        
        result = re.search('https?://(?:[a-zA-Z0-9\-]*\.)*(?:([a-zA-Z0-9\-]+\.[a-zA-Z0-9]{2,4})/?)(.*)',url)
        
        if result is None:
            return None
                
        return (result.group(1),result.group(2))
    
    def proxyRequestReceived(self):
        
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print "HTTPS is not supported at the moment!"
            self.finish()
            return
        
        url, postParameters = self.analyzeURL()
                
        analysisData = []
        analysisData.append(postParameters)
        analysisData.append("GET")
        analysisData.append("AJAX")
        
        analysisQueueEntry = {}
        analysisQueueEntry['userID'] = self._userID
        analysisQueueEntry['url'] = url
        analysisQueueEntry['data'] = analysisData
        
        analysisQueue.put(analysisQueueEntry)        

class PrivacyProxy(proxy.Proxy):
    requestFactory = PrivacyProxyRequest
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase):
        proxy.Proxy.__init__(self)
        
        self._dbHost = dbHost
        self._dbUser = dbUser
        self._dbPassword = dbPassword
        self._dbDatabase = dbDatabase

class PrivacyProxyFactory(http.HTTPFactory):
    
    _analysisThreadPool = []
    
    def __init__(self,dbHost,dbUser,dbPassword,dbDatabase,threadCount):
        http.HTTPFactory.__init__(self)
        
        self._dbHost = dbHost
        self._dbUser = dbUser
        self._dbPassword = dbPassword
        self._dbDatabase = dbDatabase
        
        log.msg("Populating thread pool")
        
        for _ in range(threadCount):
            t = AnalysisThread(dbHost,dbUser,dbPassword,dbDatabase)
            t.daemon = True
            t.start()
            self._analysisThreadPool.append(t)
            
    def __del__(self):
        log.msg("Waiting for thread pool to finish work")
        analysisQueue.join()
        log.msg("All threads finished")
    
    def buildProtocol(self, addr):
        return PrivacyProxy(self._dbHost,self._dbUser,self._dbPassword,self._dbDatabase)
    