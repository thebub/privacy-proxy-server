'''
Created on 21.05.2013

@author: dbub
'''

from twisted.application import internet, service
import ConfigParser

from net.thebub.privacyproxy.proxyserver.proxyServer import PrivacyProxyFactory
from net.thebub.privacyproxy.apiserver.apiServer import APIServerFactory

config = ConfigParser.ConfigParser()
config.readfp(open('privacyproxy.cfg'))

privacyProxyService = service.MultiService()

proxyServerProtocol = PrivacyProxyFactory(config.get("proxyServer", "dbHost"),config.get("proxyServer","dbUser"),config.get("proxyServer", "dbPassword"),config.get("proxyServer", "dbDatabase"),config.getint("proxyServer", "analysisThreadCount"))
proxyServer = internet.TCPServer(config.getint("proxyServer", "listenPort"),proxyServerProtocol)
proxyServer.setServiceParent(privacyProxyService)

apiServerProtocol = APIServerFactory(config.get("apiServer", "dbHost"),config.get("apiServer","dbUser"),config.get("apiServer", "dbPassword"),config.get("apiServer", "dbDatabase"))
apiServer = internet.TCPServer(config.getint("apiServer", "listenPort"),apiServerProtocol)
apiServer.setServiceParent(privacyProxyService)

application = service.Application("PrivacyProxy")
privacyProxyService.setServiceParent(application)
