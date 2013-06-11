'''
Created on 12.05.2013

@author: dbub
'''

from net.thebub.privacyproxy.apiserver.actions.apiAction import APIAction
from net.thebub.privacyproxy.helpers.hash import DataHashHelper

import PrivacyProxyAPI_pb2

class GetSettingsAction(APIAction):
    '''
    Get all the settings stored for the current user
    '''
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.getSettings
    
    def process(self, data):
        '''
        Get all the settings of the current user from the database and send it to the client
        '''
        self.dbConnection.query(("""SELECT user_data.id, user_data.type, user_data.description FROM user_data, user WHERE user.id = %s AND user_data.user_id = user.id;""",(self.userID,)))
        
        responseData = PrivacyProxyAPI_pb2.GetSettingsResponse()
        
        # For each entry in the database, create a response object
        for dataID, dataType, dataDescription in self.dbConnection.fetchall():
            personalData = responseData.entry.add()
            personalData.id = dataID
            personalData.type = dataType
            personalData.description = dataDescription            
        
        # Send the response
        return self._returnSuccess(responseData)

class UpdateSettingAction(APIAction,DataHashHelper):
    '''
    Update the settings of the user
    '''
    
    requiresAuthentication = True
    command = PrivacyProxyAPI_pb2.updateSetting
    
    def process(self, data):
        '''
        Parse the request and decide, which action (create/update/delete) should be executed 
        '''
    
        requestData = PrivacyProxyAPI_pb2.UpdateSettingRequest()
        requestData.ParseFromString(data)
        
        # Decide which action to be executed 
        if requestData.action == PrivacyProxyAPI_pb2.create:
            return self._create(requestData.data)
        elif requestData.action == PrivacyProxyAPI_pb2.update:
            return self._update(requestData.data)
        elif requestData.action == PrivacyProxyAPI_pb2.delete:
            return self._delete(requestData.data)
                
    def _create(self,requestData): 
        '''
        Create a new data entry in the database
        '''
               
        dataHash = self._hashData(requestData.hash)
        
        self.dbConnection.query(("""INSERT INTO user_data(user_id,type,description,hash) VALUES (%s,%s,%s,%s);""",(self.userID,requestData.type,requestData.description,dataHash)))
        
        if self.dbConnection.rowcount() == 1:
            # The entry was added successfully
            self.dbConnection.commit()
                        
            responseData = PrivacyProxyAPI_pb2.GetSettingsResponse()
            
            setting = responseData.entry.add()
            setting.id = self.dbConnection.insertid()
            setting.type = requestData.type
            setting.description = requestData.description
            
            return self._returnSuccess(responseData)
        
        # Inserting the entry was unsuccessful
        return self._returnError(PrivacyProxyAPI_pb2.forbidden)
    
    def _update(self,requestData):
        '''
        Update an existing entry in the databse
        '''
        
        dataHash = self._hashData(requestData.hash)
        
        self.dbConnection.query(("""UPDATE user_data SET user_data.description = %s, user_data.hash = %s WHERE user_data.id = %s AND user_data.user_id = %s;""",(requestData.description,dataHash,requestData.id,self.userID)))
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
                        
            return self._returnSuccess()
        
        return self._returnError(PrivacyProxyAPI_pb2.forbidden)
    
    def _delete(self,requestData):
        '''
        Remove an entry from the database
        '''
        
        self.dbConnection.query(("""DELETE FROM user_data WHERE user_data.id = %s AND user_data.user_id = %s;""",(requestData.id,self.userID)))
        
        if self.dbConnection.rowcount() == 1:
            self.dbConnection.commit()
                        
            return self._returnSuccess()
        
        return self._returnError(PrivacyProxyAPI_pb2.forbidden)