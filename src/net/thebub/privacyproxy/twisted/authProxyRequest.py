'''
Created on 20.05.2013

@author: dbub
'''

from twisted.web import proxy

import base64

class AuthProxyRequest(proxy.ProxyRequest):
    '''
    This class provides a proxy request implementation, which checks for user authentication.
    '''
    _realmName = None
    
    def requiresUserAuth(self):
        raise NotImplementedError()
    
    def checkUserAuth(self,username,password):
        raise NotImplementedError()
    
    def proxyRequestReceived(self):
        raise NotImplementedError()
    
    def _returnError(self):
        '''
        Indicate an usuccessful authentication attempt.
        '''
        if self._realmName is not None:
            self.setHeader("Proxy-Authenticate", "Basic realm=\"" + self._realmName+"\"")
        else:
            self.setHeader("Proxy-Authenticate", "Basic")
        self.setResponseCode(407)
        self.responseHeaders.addRawHeader("Content-Type", "text/html")
        self.write("<H1>Please authenticate</H1>")

    def process(self):
        '''
        Check the request for a successful authentication
        '''
        authentication = self.getHeader("Proxy-Authorization")
        
        if self.requiresUserAuth() and authentication is None:
            self._returnError()
            self.finish()
            
        elif self.requiresUserAuth() and authentication is not None:
            # Check the support of the authentication scheme
            if authentication.find("Basic") == -1:
                self._returnError()
                self.finish()
            else:
                # Split and decode the authentication data
                authData = authentication.split()[1]
                authString = base64.decodestring(authData)
                authFields = authString.split(":")
                
                # Check the authentication and process request
                if not self.checkUserAuth(authFields[0], authFields[1]):
                    self._returnError()
                    self.finish()
                else:
                    self.proxyRequestReceived()
        return