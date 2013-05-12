'''
Created on 12.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.actions.apiAction import APIAction,PasswordHelper
from net.thebub.privacyproxy.actions.sessionActions import LoginAction
import APICall_pb2

import MySQLdb

class CreateUserAction(APIAction,PasswordHelper):    
        
    command = APICall_pb2.createUser
    
    def process(self, data):
        requestData = APICall_pb2.CreateUserRequest()
        requestData.ParseFromString(data)
        
        try:
            hashedPassword,salt = self._hashPassword(requestData.password, createSalt=True)
        
            self.protocol.dbConnection.query(("""INSERT INTO user(username,password,email,user_salt) VALUES (%s,%s,%s,%s)""",(requestData.username,hashedPassword,requestData.email,salt)))
        except ValueError:
            return self._returnError(APICall_pb2.forbidden)
        except MySQLdb.IntegrityError:            
            return self._returnError(APICall_pb2.forbidden)
        
        if self.protocol.dbConnection.rowcount() == 1:
            self.protocol.dbConnection.commit()
            
            loginData = APICall_pb2.LoginData()
            loginData.username = requestData.username
            loginData.password = requestData.password
            
            login = LoginAction(self.protocol)
            return login.process(loginData.SerializeToString())
        else:
            return self._returnError(APICall_pb2.forbidden)
    
class UpdateUserAction(APIAction,PasswordHelper):    
        
    requiresAuthentication = True
    command = APICall_pb2.updateUser
    
    def process(self, data):        
        requestData = APICall_pb2.UpdateUserRequest()
        requestData.ParseFromString(data)
                
        if requestData.HasField('password'):
            try:
                hashedPassword = self._hashPassword(requestData.password)[0]
            except ValueError:
                return self._returnError(APICall_pb2.forbidden)
        
        if requestData.HasField('password') and requestData.HasField('email'):
            self.protocol.dbConnection.query(("""UPDATE user SET password = %s, email = %s WHERE id = %s;""",(hashedPassword,requestData.email,self.protocol.userID)))
        elif requestData.HasField('password') and not requestData.HasField('email'):
            self.protocol.dbConnection.query(("""UPDATE user SET password = %s WHERE id = %s;""",(hashedPassword,self.protocol.userID)))
        elif not requestData.HasField('password') and requestData.HasField('email'):
            self.protocol.dbConnection.query(("""UPDATE user SET email = %s WHERE id = %s;""",(requestData.email,self.protocol.userID)))
                
        if self.protocol.dbConnection.rowcount() == 1:
            self.protocol.dbConnection.commit()
            return self._returnSuccess()

        return self._returnError(APICall_pb2.forbidden)
    
class DeleteUserAction(APIAction,PasswordHelper):    
    
    requiresAuthentication = True
    command = APICall_pb2.deleteUser
    
    def process(self, data):
        requestData = APICall_pb2.DeleteUserRequest()
        requestData.ParseFromString(data)
        
        self.protocol.dbConnection.query(("""SELECT id,password,user_salt FROM user WHERE id = %s;""",(self.protocol.userID,)))
                
        if self.protocol.dbConnection.rowcount() == 1:            
            result = self.protocol.dbConnection.fetchone()
                        
            if self._verifyPassword(requestData.password, result[1], result[2]):
                self.protocol.dbConnection.query(("""DELETE FROM user WHERE id = %s;""",(self.protocol.userID,)))
                self.protocol.dbConnection.commit()
                
                return self._returnSuccess()
        
        return self._returnError(APICall_pb2.unauthorized)