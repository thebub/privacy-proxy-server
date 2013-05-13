'''
Created on 12.05.2013

@author: dbub
'''

import common,time
import APICall_pb2

if __name__ == '__main__':
    c = APICall_pb2.CreateUserRequest()
    c.username = "test"
    c.password = "test123"
    c.email = "test@test.com"
        
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.createUser
    a.arguments = c.SerializeToString()
    
    test = common.Test("Successful user creation", a, expectedSuccess=True,requestClass=APICall_pb2.CreateUserRequest,responseClass=APICall_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    test = common.Test("Unsuccessful user creation", a, expectedSuccess=False,expectedError=APICall_pb2.forbidden,requestClass=APICall_pb2.CreateUserRequest)
    test.run()
    
    timeout = 10
    print "### Sleeping for",timeout,"seconds ###"
    time.sleep(timeout)
    print "### Sleeping done ###\n"
    
    u = APICall_pb2.UpdateUserRequest()
    u.email = "test@qwertz.com"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.updateUser
    a.sessionKey = sessionID
    a.arguments = u.SerializeToString()
    
    test = common.Test("Successful user update (email)", a, expectedSuccess=True,requestClass=APICall_pb2.UpdateUserRequest)
    test.run()
    
    timeout = 10
    print "### Sleeping for",timeout,"seconds ###"
    time.sleep(timeout)
    print "### Sleeping done ###\n"
    
    u.password = "test321"
    
    a.arguments = u.SerializeToString()
    
    test = common.Test("Successful user update (email & password)", a, expectedSuccess=True,requestClass=APICall_pb2.UpdateUserRequest)
    test.run()    
    
    d = APICall_pb2.DeleteUserRequest()
    d.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.deleteUser
    a.arguments = d.SerializeToString()
    a.sessionKey = sessionID
    
    test = common.Test("Unsuccessful user deletion", a, expectedSuccess=False,expectedError=APICall_pb2.unauthorized,requestClass=APICall_pb2.DeleteUserRequest)
    test.run()
    
    d = APICall_pb2.DeleteUserRequest()
    d.password = "test321"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.deleteUser
    a.arguments = d.SerializeToString()
    a.sessionKey = sessionID
    
    test = common.Test("Successful user deletion", a, expectedSuccess=True,requestClass=APICall_pb2.DeleteUserRequest)
    test.run()