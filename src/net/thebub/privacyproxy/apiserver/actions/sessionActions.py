'''
Created on 09.05.2013

@author: dbub
'''

import uuid

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction
from net.thebub.privacyproxy.helpers.password import PasswordHelper

import APICall_pb2

class LoginAction(APIAction,PasswordHelper):

    command = APICall_pb2.login

    def process(self, data):
        requestData = APICall_pb2.LoginData()
        requestData.ParseFromString(data)
        
        self.dbConnection.query(("""SELECT id,username,password,password_salt FROM user WHERE username = %s """,(requestData.username,)))
                
        if self.dbConnection.rowcount() == 1:
            result = self.dbConnection.fetchone()
                       
            if self._verifyPassword(requestData.password, result[2], result[3]):
                sessionID = uuid.uuid4().hex
                
                self.dbConnection.query(("""INSERT INTO session(user_id,session_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE session_id = %s""",(result[0],sessionID,sessionID)))
                
                if self.dbConnection.rowcount() == 1 or self.dbConnection.rowcount() == 2:
                    self.dbConnection.commit()
                                        
                    responseData = APICall_pb2.LoginResponse()
                    responseData.username = requestData.username
                    responseData.sessionID = sessionID
                                        
                    return self._returnSuccess(responseData)
        
        return self._returnError(APICall_pb2.unauthorized)
    
class LogoutAction(APIAction):    
    
    requiresAuthentication = True
    command = APICall_pb2.logout
    
    def process(self, data):
        self.dbConnection.query(("""DELETE FROM session WHERE session_id = %s AND user_id = %s;""",(self.sessionID,self.userID)))
        self.dbConnection.commit()
                
        return self._returnSuccess()