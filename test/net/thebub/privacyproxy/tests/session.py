'''
Created on 10.05.2013

@author: dbub
'''

import common
import PrivacyProxyAPI_pb2

if __name__ == '__main__':
    l = PrivacyProxyAPI_pb2.LoginData()
    l.username = "admin"
    l.password = "stupid"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Unsuccessful login", a, expectedSuccess=False,expectedError=PrivacyProxyAPI_pb2.unauthorized,requestClass=PrivacyProxyAPI_pb2.LoginData)
    responseData = test.run()
    
    l = PrivacyProxyAPI_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.LoginData,responseClass=PrivacyProxyAPI_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Unsuccessful logout", a, expectedSuccess=False,expectedError=PrivacyProxyAPI_pb2.unauthorized)
    test.run()