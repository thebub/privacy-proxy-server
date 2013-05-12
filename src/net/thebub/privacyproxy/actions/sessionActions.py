'''
Created on 09.05.2013

@author: dbub
'''

import uuid

from net.thebub.privacyproxy.actions.apiAction import APIAction,PasswordHelper
import APICall_pb2

class LoginAction(APIAction,PasswordHelper):

    command = APICall_pb2.login

    def process(self, data):
        requestData = APICall_pb2.LoginData()
        requestData.ParseFromString(data)
        
        self.protocol.dbConnection.query(("""SELECT id,username,password,user_salt FROM user WHERE username = %s """,(requestData.username,)))
                
        if self.protocol.dbConnection.rowcount() == 1:
            result = self.protocol.dbConnection.fetchone()
                       
            if self._verifyPassword(requestData.password, result[2], result[3]):
                sessionID = uuid.uuid4().hex
                
                self.protocol.dbConnection.query(("""INSERT INTO session(user_id,session_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE session_id = %s""",(result[0],sessionID,sessionID)))
                
                if self.protocol.dbConnection.rowcount() == 1 or self.protocol.dbConnection.rowcount() == 2:
                    self.protocol.dbConnection.commit()
                                        
                    responseData = APICall_pb2.LoginResponse()
                    responseData.username = requestData.username
                    responseData.sessionID = sessionID
                                        
                    return self._returnSuccess(responseData)
        
        return self._returnError(APICall_pb2.unauthorized)
    
class LogoutAction(APIAction):    
    
    requiresAuthentication = True
    command = APICall_pb2.logout
    
    def process(self, data):
        self.protocol.dbConnection.query(("""DELETE FROM session WHERE session_id = %s AND user_id = %s;""",(self.protocol.sessionID,self.protocol.userID)))
        self.protocol.dbConnection.commit()
                
        return self._returnSuccess()