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
    
    test = common.Test("Creating connection - unsuccessful login", a, expectedSuccess=False,expectedError=APICall_pb2.unauthorized,requestClass=APICall_pb2.LoginData)
    responseData = test.run()
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    timeout = 60
    print "### Sleeping for",timeout,"seconds ###"
    time.sleep(timeout)
    print "### Sleeping done ###\n"
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "stupid"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Testing SQL - unsuccessful login", a, expectedSuccess=False,expectedError=APICall_pb2.unauthorized,requestClass=APICall_pb2.LoginData)
    responseData = test.run()