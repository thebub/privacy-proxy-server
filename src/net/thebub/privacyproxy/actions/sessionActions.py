'''
Created on 09.05.2013

@author: dbub
'''

import hashlib, uuid, string

from net.thebub.privacyproxy.actions.apiAction import APIAction
import APICall_pb2

class LoginAction(APIAction):

    def process(self, data):
        requestData = APICall_pb2.LoginData()
        requestData.ParseFromString(data)
        
        self.protocol.dbConnection.query(("""SELECT id,username,password,user_salt FROM user WHERE username = %s """,(requestData.username,)))
        result = self.protocol.dbConnection.fetchone()
        
        hashAlgorithm = hashlib.sha256()
        saltedPassword = string.join([requestData.password,result[3]],"")
        hashAlgorithm.update(saltedPassword)
        passwordHash = hashAlgorithm.hexdigest()
        
        response = APICall_pb2.APIResponse()
        response.command = APICall_pb2.login
        
        if passwordHash == result[2]:
            sessionID = uuid.uuid4().hex
            
            self.protocol.dbConnection.query(("""INSERT INTO session(user_id,session_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE session_id = %s""",(result[0],sessionID,sessionID)))
            self.protocol.dbConnection.commit()
            
            if self.protocol.dbConnection.rowcount() == 1 or self.protocol.dbConnection.rowcount() == 2:
                response.success = True
                response.errorCode = APICall_pb2.none
                
                responseData = APICall_pb2.LoginResponse()
                responseData.username = requestData.username
                responseData.sessionID = sessionID
                
                response.data = responseData.SerializeToString()
                
            else:                
                response.success = False
                response.errorCode = APICall_pb2.unauthorized
        else:
            response.success = False
            response.errorCode = APICall_pb2.unauthorized
        
        return response
    
class LogoutAction(APIAction):    
        
    def __init__(self,protocol):
        super(LogoutAction,self).__init__(protocol)
        self.requiresAuthentication = True
        pass
    
    def process(self, data):
        self.protocol.dbConnection.query(("""DELETE FROM session WHERE session_id = %s;""",(self.protocol.sessionKey,)))
        self.protocol.dbConnection.commit()
        
        response = APICall_pb2.APIResponse()
        response.command = APICall_pb2.logout
        response.success = True
        response.errorCode = APICall_pb2.none
        
        return response