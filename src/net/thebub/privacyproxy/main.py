'''
Created on 08.05.2013

@author: dbub
'''

from twisted.web import proxy, http
from twisted.internet import reactor

from twisted.python import log
import sys
 
class PrivacyProxyRequest(proxy.ProxyRequest):
    def process(self):
        """
        It's normal to see a blank HTTPS page. As the proxy only works
        with the HTTP protocol.
        """
        print "Request from %s for %s" % (
            self.getClientIP(), self.getAllHeaders()['host'])
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print "HTTPS is not supported at the moment!"

class LoggingProxy(proxy.Proxy):
    requestFactory = PrivacyProxyRequest

class LoggingProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return LoggingProxy()




if __name__ == '__main__':
    log.startLogging(sys.stdout)
    
    reactor.listenTCP(8080, LoggingProxyFactory())
    reactor.run()