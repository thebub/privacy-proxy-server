'''
Created on 10.05.2013

@author: dbub
'''

import common
import APICall_pb2

if __name__ == '__main__':
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "stupid"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Unsuccessful login", a, expectedSuccess=False,expectedError=APICall_pb2.unauthorized,requestClass=APICall_pb2.LoginData)
    responseData = test.run()
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=APICall_pb2.LoginData,responseClass=APICall_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Unsuccessful logout", a, expectedSuccess=False,expectedError=APICall_pb2.unauthorized)
    test.run()