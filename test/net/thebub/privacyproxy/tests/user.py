'''
Created on 12.05.2013

@author: dbub
'''

import common,time
import PrivacyProxyAPI_pb2

if __name__ == '__main__':
    c = PrivacyProxyAPI_pb2.CreateUserRequest()
    c.username = "test"
    c.password = "test123"
    c.email = "test@test.com"
        
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.createUser
    a.arguments = c.SerializeToString()
    
    test = common.Test("Successful user creation", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.CreateUserRequest,responseClass=PrivacyProxyAPI_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    test = common.Test("Unsuccessful user creation", a, expectedSuccess=False,expectedError=PrivacyProxyAPI_pb2.forbidden,requestClass=PrivacyProxyAPI_pb2.CreateUserRequest)
    test.run()
    
    timeout = 10
    print "### Sleeping for",timeout,"seconds ###"
    time.sleep(timeout)
    print "### Sleeping done ###\n"
    
    u = PrivacyProxyAPI_pb2.UpdateUserRequest()
    u.email = "test@qwertz.com"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.updateUser
    a.sessionKey = sessionID
    a.arguments = u.SerializeToString()
    
    test = common.Test("Successful user update (email)", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.UpdateUserRequest)
    test.run()
    
    timeout = 10
    print "### Sleeping for",timeout,"seconds ###"
    time.sleep(timeout)
    print "### Sleeping done ###\n"
    
    u.password = "test321"
    
    a.arguments = u.SerializeToString()
    
    test = common.Test("Successful user update (email & password)", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.UpdateUserRequest)
    test.run()    
    
    d = PrivacyProxyAPI_pb2.DeleteUserRequest()
    d.password = "bla"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.deleteUser
    a.arguments = d.SerializeToString()
    a.sessionKey = sessionID
    
    test = common.Test("Unsuccessful user deletion", a, expectedSuccess=False,expectedError=PrivacyProxyAPI_pb2.unauthorized,requestClass=PrivacyProxyAPI_pb2.DeleteUserRequest)
    test.run()
    
    d = PrivacyProxyAPI_pb2.DeleteUserRequest()
    d.password = "test321"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.deleteUser
    a.arguments = d.SerializeToString()
    a.sessionKey = sessionID
    
    test = common.Test("Successful user deletion", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.DeleteUserRequest)
    test.run()