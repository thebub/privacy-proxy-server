'''
Created on 10.05.2013

@author: dbub
'''

import common
import APICall_pb2

if __name__ == '__main__':
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=APICall_pb2.LoginData,responseClass=APICall_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getWebpages
    a.sessionKey = sessionID
    
    test = common.Test("Get websites", a, expectedSuccess=True, responseClass=APICall_pb2.WebLogWebsitesResponse)
    websites = test.run()
    
    w = APICall_pb2.WebLogWebsiteDataRequest()
    w.id = websites.pages[0].id
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getWebpageData
    a.sessionKey = sessionID
    a.arguments = w.SerializeToString()
    
    test = common.Test("Get website data", a, expectedSuccess=True, responseClass=APICall_pb2.WebLogWebsiteDataResponse)
    test.run()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()