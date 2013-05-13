'''
Created on 12.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction
from net.thebub.privacyproxy.helpers.hash import DataHashHelper

import APICall_pb2

class GetSettingsAction(APIAction):
    
    requiresAuthentication = True
    command = APICall_pb2.getSettings
    
    def process(self, data):        
        self.dbConnection.query(("""SELECT user_data.id, user_data.type, user_data.description FROM user_data, user WHERE user.id = %s AND user_data.user_id = user.id;""",(self.userID,)))
        
        responseData = APICall_pb2.GetSettingsResponse()
        
        for dataID, dataType, dataDescription in self.dbConnection.fetchall():
            personalData = responseData.entry.add()
            personalData.id = dataID
            personalData.type = dataType
            personalData.description = dataDescription            
        
        return self._returnSuccess(responseData)

class UpdateSettingAction(APIAction,DataHashHelper):    
    
    requiresAuthentication = True
    command = APICall_pb2.updateSetting
    
    def process(self, data):
        requestData = APICall_pb2.UpdateSettingRequest()
        requestData.ParseFromString(data)
        
        if requestData.action == APICall_pb2.create:
            return self._create(requestData.data)
        elif requestData.action == APICall_pb2.update:
            return self._update(requestData.data)
        elif requestData.action == APICall_pb2.delete:
            return self._delete(requestData.data)
                
    def _create(self,requestData):        
        dataHash = self._hashData(requestData.hash)
        
        self.dbConnection.query(("""INSERT INTO user_data(user_id,type,description,hash) VALUES (%s,%s,%s,%s);""",(self.userID,requestData.type,requestData.description,dataHash)))
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
                        
            responseData = APICall_pb2.GetSettingsResponse()
            
            setting = responseData.entry.add()
            setting.id = self.dbConnection.insertid()
            setting.type = requestData.type
            setting.description = requestData.description
            
            return self._returnSuccess(responseData)
        
        return self._returnError(APICall_pb2.forbidden)
    
    def _update(self,requestData):
        dataHash = self._hashData(requestData.hash)
        
        self.dbConnection.query(("""UPDATE user_data SET user_data.description = %s, user_data.hash = %s WHERE user_data.id = %s AND user_data.user_id = %s;""",(requestData.description,dataHash,requestData.id,self.userID)))
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
                        
            return self._returnSuccess()
        
        return self._returnError(APICall_pb2.forbidden)
    
    def _delete(self,requestData):        
        self.dbConnection.query(("""DELETE FROM user_data WHERE user_data.id = %s AND user_data.user_id = %s;""",(requestData.id,self.userID)))
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
                        
            return self._returnSuccess()
        
        return self._returnError(APICall_pb2.forbidden)