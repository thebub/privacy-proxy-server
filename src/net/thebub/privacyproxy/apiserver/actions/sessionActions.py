'''
Created on 09.05.2013

@author: dbub
'''

import uuid

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction
from net.thebub.privacyproxy.helpers.password import PasswordHelper

import PrivacyProxyAPI_pb2

class LoginAction(APIAction,PasswordHelper):
    '''
    This action provides the login action for creating a valid session ID
    '''

    command = PrivacyProxyAPI_pb2.login

    def process(self, data):
        '''
        Login the user using the supplied data
        '''
        
        # Parse the legin request
        requestData = PrivacyProxyAPI_pb2.LoginData()
        requestData.ParseFromString(data)
        
        # Get the user data from database
        self.dbConnection.query(("""SELECT id,username,password,password_salt FROM user WHERE username = %s """,(requestData.username,)))
                
        if self.dbConnection.rowcount() == 1:
            # USer found in database
            result = self.dbConnection.fetchone()
                       
            if self._verifyPassword(requestData.password, result[2], result[3]):
                # Verified credentials successfully. Create a session ID and store it in the DB
                sessionID = uuid.uuid4().hex
                
                self.dbConnection.query(("""INSERT INTO session(user_id,session_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE session_id = %s""",(result[0],sessionID,sessionID)))
                
                if self.dbConnection.rowcount() == 1 or self.dbConnection.rowcount() == 2:
                    # Login was successful
                    self.dbConnection.commit()
                                        
                    responseData = PrivacyProxyAPI_pb2.LoginResponse()
                    responseData.username = requestData.username
                    responseData.sessionID = sessionID
                                        
                    # Login was successful. Send the response with the session ID
                    return self._returnSuccess(responseData)
        
        # The login was unsuccessful. Return an unauthorized message
        return self._returnError(PrivacyProxyAPI_pb2.unauthorized)
    
class LogoutAction(APIAction):
    '''
    This action destroys the current session of the user
    ''' 
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.logout
    
    def process(self, data):
        '''
        Destroy the session entry in the datbase
        '''
        self.dbConnection.query(("""DELETE FROM session WHERE session_id = %s AND user_id = %s;""",(self.sessionID,self.userID)))
        self.dbConnection.commit()
                
        return self._returnSuccess()