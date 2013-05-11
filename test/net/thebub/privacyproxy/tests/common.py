'''
Created on 11.05.2013

@author: dbub
'''

import socket
import APICall_pb2

class Connection(object):
    
    def __init__(self):
        super(Connection,self).__init__()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("127.0.0.1",8081))
        
        pass
    
    def __del__(self):
        self.socket.close()
        pass
    
    def sendMessage(self,message):
        self.socket.sendall(message.SerializeToString())
    
        data = self.socket.recv(1024)
        
        r = APICall_pb2.APIResponse()
        r.ParseFromString(data)
        
        return r
    
class TestSummary():
    
    def __init__(self):
        self.tests = 0
        self.testsSuccessful = 0
        self.testsFailed = 0
        
    def __del__(self):
        print "### Test summary ###"
        print "Tests run:\t\t",self.tests
        print "Successful tests:\t",self.testsSuccessful
        print "Failed tests:\t\t",self.testsFailed
        
    def testRun(self,testSuccess):
        self.tests += 1
        if testSuccess:
            self.testsSuccessful += 1
        else:
            self.testsFailed += 1            
    
class Test():
    
    connection = Connection()
    summary = TestSummary()
    
    def __init__(self,title,message,expectedResult,responseClass = None):
        self.title = title
        self.message = message
        self.expectedResult = expectedResult
        self.responseClass = responseClass
                
    def run(self):
        print "### Running test:",self.title,"###\n"
        
        print "Sending the following request:\n",self.message.__str__()
        
        self.response = Test.connection.sendMessage(self.message)
            
        print "Received the following response:\n",self.response.__str__()
        
        if self.responseClass is not None:
            self.responseData = self.responseClass()
            self.responseData.ParseFromString(self.response.data)
            
            print "Received the following response data:\n",self.responseData.__str__()
        
        if self.response.success == self.expectedResult:
            print "# Test was successful! #\n"
            Test.summary.testRun(True)
        else:
            print "# Test was unsuccessful! #\n"
            Test.summary.testRun(False)
        
        print "### Test completed ###\n"
        
        if hasattr(self, "responseData"):
            return self.responseData