'''
Created on 10.05.2013

@author: dbub
'''

import common
import PrivacyProxyAPI_pb2

if __name__ == '__main__':
    l = PrivacyProxyAPI_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.LoginData,responseClass=PrivacyProxyAPI_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getWebpages
    a.sessionKey = sessionID
    
    test = common.Test("Get websites", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.WebLogWebsitesResponse)
    websites = test.run()
    
    w = PrivacyProxyAPI_pb2.WebLogWebsiteDataRequest()
    w.id = websites.pages[0].id
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getWebpageData
    a.sessionKey = sessionID
    a.arguments = w.SerializeToString()
    
    test = common.Test("Get website data", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.WebLogWebsiteDataResponse)
    test.run()
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()