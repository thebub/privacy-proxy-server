'''
Created on 21.05.2013

@author: dbub
'''

from twisted.application import internet, service
import ConfigParser

from net.thebub.privacyproxy.proxyserver.proxyServer import PrivacyProxyFactory
from net.thebub.privacyproxy.apiserver.apiServer import APIServerFactory

# Load the config parser and let it parse the config file
config = ConfigParser.ConfigParser()
config.readfp(open('privacyproxy.cfg'))

# Instantiate the multi-service hostign different services
privacyProxyService = service.MultiService()

# Configure the proxy server protocol and add it to the multi-service
proxyServerProtocol = PrivacyProxyFactory(config.get("proxyServer", "dbHost"),config.get("proxyServer","dbUser"),config.get("proxyServer", "dbPassword"),config.get("proxyServer", "dbDatabase"),config.getint("proxyServer", "analysisThreadCount"))
proxyServer = internet.TCPServer(config.getint("proxyServer", "listenPort"),proxyServerProtocol)
proxyServer.setServiceParent(privacyProxyService)

# Configure the API server protocol and add it to the multi-service
apiServerProtocol = APIServerFactory(config.get("apiServer", "dbHost"),config.get("apiServer","dbUser"),config.get("apiServer", "dbPassword"),config.get("apiServer", "dbDatabase"))
apiServer = internet.TCPServer(config.getint("apiServer", "listenPort"),apiServerProtocol)
apiServer.setServiceParent(privacyProxyService)

# Start the application
application = service.Application("PrivacyProxy")
privacyProxyService.setServiceParent(application)
