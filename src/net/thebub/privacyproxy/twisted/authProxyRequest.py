'''
Created on 20.05.2013

@author: dbub
'''

from twisted.web import proxy

import base64

class AuthProxyRequest(proxy.ProxyRequest):
    _realmName = None
    
    def requiresUserAuth(self):
        raise NotImplementedError()
    
    def checkUserAuth(self,username,password):
        raise NotImplementedError()
    
    def proxyRequestReceived(self):
        raise NotImplementedError()
    
    def _returnError(self):
        if self._realmName is not None:
            self.setHeader("Proxy-Authenticate", "Basic realm=\"" + self._realmName+"\"")
        else:
            self.setHeader("Proxy-Authenticate", "Basic")
        self.setResponseCode(407)
        self.responseHeaders.addRawHeader("Content-Type", "text/html")
        self.write("<H1>Please authenticate</H1>")

    def process(self):        
        authentication = self.getHeader("Proxy-Authorization")
        
        if self.requiresUserAuth() and authentication is None:
            self._returnError()
            self.finish()
            
        elif self.requiresUserAuth() and authentication is not None:
            if authentication.find("Basic") == -1:
                self._returnError()
                self.finish()
            else:
                authData = authentication.split()[1]
                authString = base64.decodestring(authData)
                authFields = authString.split(":")
                                
                if not self.checkUserAuth(authFields[0], authFields[1]):
                    self._returnError()
                    self.finish()
                else:
                    self.proxyRequestReceived()
        return