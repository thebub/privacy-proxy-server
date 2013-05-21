'''
Created on 12.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction
from net.thebub.privacyproxy.apiserver.actions.sessionActions import LoginAction
from net.thebub.privacyproxy.helpers.password import PasswordHelper
from net.thebub.privacyproxy.helpers.hash import DataHashHelper

import PrivacyProxyAPI_pb2

import MySQLdb

class CreateUserAction(APIAction,PasswordHelper,DataHashHelper):    
        
    command = PrivacyProxyAPI_pb2.createUser
        
    def process(self, data):
        requestData = PrivacyProxyAPI_pb2.CreateUserRequest()
        requestData.ParseFromString(data)
        
        try:
            hashedPassword,salt = self._hashPassword(requestData.password, createSalt=True)
            dataSalt = self._createDataSalt()
        
            self.dbConnection.query(("""INSERT INTO user(username,password,email,password_salt,data_salt) VALUES (%s,%s,%s,%s,%s)""",(requestData.username,hashedPassword,requestData.email,salt,dataSalt)))
        except ValueError:
            return self._returnError(PrivacyProxyAPI_pb2.forbidden)
        except MySQLdb.IntegrityError:            
            return self._returnError(PrivacyProxyAPI_pb2.forbidden)
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
            
            loginData = PrivacyProxyAPI_pb2.LoginData()
            loginData.username = requestData.username
            loginData.password = requestData.password
            
            login = LoginAction(self.dbConnection,self.userID,self.sessionID)
            return login.process(loginData.SerializeToString())
        else:
            return self._returnError(PrivacyProxyAPI_pb2.forbidden)
    
class UpdateUserAction(APIAction,PasswordHelper):    
        
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.updateUser
    
    def process(self, data):        
        requestData = PrivacyProxyAPI_pb2.UpdateUserRequest()
        requestData.ParseFromString(data)
                
        if requestData.HasField('password'):
            try:
                hashedPassword = self._hashPassword(requestData.password)[0]
            except ValueError:
                return self._returnError(PrivacyProxyAPI_pb2.forbidden)
        
        if requestData.HasField('password') and requestData.HasField('email'):
            self.dbConnection.query(("""UPDATE user SET password = %s, email = %s WHERE id = %s;""",(hashedPassword,requestData.email,self.userID)))
        elif requestData.HasField('password') and not requestData.HasField('email'):
            self.dbConnection.query(("""UPDATE user SET password = %s WHERE id = %s;""",(hashedPassword,self.userID)))
        elif not requestData.HasField('password') and requestData.HasField('email'):
            self.dbConnection.query(("""UPDATE user SET email = %s WHERE id = %s;""",(requestData.email,self.userID)))
                
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
            return self._returnSuccess()

        return self._returnError(PrivacyProxyAPI_pb2.forbidden)
    
class DeleteUserAction(APIAction,PasswordHelper):    
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.deleteUser
    
    def process(self, data):
        requestData = PrivacyProxyAPI_pb2.DeleteUserRequest()
        requestData.ParseFromString(data)
        
        self.dbConnection.query(("""SELECT id,password,password_salt FROM user WHERE id = %s;""",(self.userID,)))
                
        if self.dbConnection.rowcount() == 1:            
            result = self.dbConnection.fetchone()
                        
            if self._verifyPassword(requestData.password, result[1], result[2]):
                self.dbConnection.query(("""DELETE FROM user WHERE id = %s;""",(self.userID,)))
                self.dbConnection.commit()
                
                return self._returnSuccess()
        
        return self._returnError(PrivacyProxyAPI_pb2.unauthorized)