'''
Created on 10.05.2013

@author: dbub
'''

import time
import common
import APICall_pb2

if __name__ == '__main__':
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "stupid"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Unsuccessful login", a, False)
    responseData = test.run()
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, True, APICall_pb2.LoginResponse)
    responseData = test.run()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = responseData.sessionID
    
    test = common.Test("Successful logout", a, True)
    test.run()
    
    time.sleep(30)
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "stupid"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("SQL connection timeout", a, False)
    responseData = test.run()