'''
Created on 09.05.2013

@author: dbub
'''

from twisted.python import log

import MySQLdb, hashlib, uuid

from net.thebub.privacyproxy.actions.apiAction import APIAction
import APICall_pb2

class LoginAction(APIAction):

    def process(self, data):
        requestData = APICall_pb2.LoginData()
        requestData.ParseFromString(data)
        
        self.protocol.dbCursor.execute("""SELECT id,username,password,user_salt FROM user WHERE username = %s """,(requestData.username,))
        result = self.protocol.dbCursor.fetchone()
        
        hashAlgorithm = hashlib.sha256()
        passwordHash = hashAlgorithm.update(requestData.pasword + result[3]).hexdigest()
        
        response = APICall_pb2.APIResponse()
        
        if passwordHash == result[2]:
            
            
            sessionID = uuid.uuid4().hex
            
            self.protocol.dbCursor.execute("""INSERT INTO session(user_id,session_id) VALUES (%s,%s) ON DUPLICATE KEY UPDATE session_id = %s""",(result[0],sessionID,sessionID))
            
            if self.protocol.dbCursor.rowcount == 1:
                response.success = True
                response.errorCode = APICall_pb2.none
            else:                
                response.success = False
                response.errorCode = APICall_pb2.unauthorized
        else:
            response.success = False
            response.errorCode = APICall_pb2.unauthorized
        
        return response
    
class LogoutAction(APIAction):    
        
    def __init__(self,protocol):
        super(LogoutAction,self).__init__(self,protocol)
        self.requiresAuthentication = True
        pass
    
    def process(self, data):
        self.protocol.dbCursor.execute("""DELETE FROM session WHERE session.hash = %s;""",(self.protocol.sessionKey,))
        
        response = APICall_pb2.APIResponse()
        response.command = APICall_pb2.logout
        response.success = True
        response.errorCode = APICall_pb2.none
        
        return response