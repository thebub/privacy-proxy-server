'''
Created on 21.05.2013

@author: dbub
'''

from twisted.application import internet, service

from net.thebub.privacyproxy.proxyserver.proxyServer import PrivacyProxyFactory
from net.thebub.privacyproxy.apiserver.apiServer import APIServerFactory

# Create a MultiService, and hook up a TCPServer and a UDPServer to it as
# children.
privacyProxyService = service.MultiService()

internet.TCPServer(8080, PrivacyProxyFactory()).setServiceParent(privacyProxyService)
internet.TCPServer(8081, APIServerFactory("thebub.net","privacyproxy","seemoo!delphine")).setServiceParent(privacyProxyService)

# Create an application as normal
application = service.Application("PrivacyProxy")
# Connect our MultiService to the application, just like a normal service.
privacyProxyService.setServiceParent(application)