'''
Created on 10.05.2013

@author: dbub
'''

import socket

import APICall_pb2

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1",8081))
    
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    s.sendall(a.SerializeToString())
    
    data = s.recv(1024)
    
    r = APICall_pb2.APIResponse()
    r.ParseFromString(data)
    
    rr = APICall_pb2.LoginResponse()
    rr.ParseFromString(r.data)
    
    print 'Received response:\n', r.__str__()
    print 'Received response-data:\n', rr.__str__()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = rr.sessionID
    
    s.sendall(a.SerializeToString())
    
    data = s.recv(1024)
    
    r = APICall_pb2.APIResponse()
    r.ParseFromString(data)
    
    print 'Received response:\n', r.__str__()
    
    s.close()