'''
Created on 10.05.2013

@author: dbub
'''

import common
import APICall_pb2

if __name__ == '__main__':
    l = APICall_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=APICall_pb2.LoginData,responseClass=APICall_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=APICall_pb2.GetSettingsResponse)
    old_settings = test.run()
    
    s = APICall_pb2.UpdateSettingRequest()
    s.action = APICall_pb2.create
    s.data.type = APICall_pb2.creditcard
    s.data.description = "Test 123"
    s.data.hash = "fuuu"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Create setting", a, expectedSuccess=True,requestClass=APICall_pb2.UpdateSettingRequest,responseClass=APICall_pb2.GetSettingsResponse)
    new_setting_id = test.run().entry[0].id
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=APICall_pb2.GetSettingsResponse)
    test.run()    
    
    s = APICall_pb2.UpdateSettingRequest()
    s.action = APICall_pb2.update
    s.data.id = new_setting_id
    s.data.type = APICall_pb2.creditcard
    s.data.description = "Test 321"
    s.data.hash = "lolol"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Update setting", a, expectedSuccess=True,requestClass=APICall_pb2.UpdateSettingRequest)
    test.run()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=APICall_pb2.GetSettingsResponse)
    test.run()
    
    s = APICall_pb2.UpdateSettingRequest()
    s.action = APICall_pb2.delete
    s.data.id = new_setting_id
    s.data.type = APICall_pb2.creditcard
    s.data.description = "Test 321"
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Remove setting", a, expectedSuccess=True,requestClass=APICall_pb2.UpdateSettingRequest)
    test.run()
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=APICall_pb2.GetSettingsResponse)
    test.run()    
    
    a = APICall_pb2.APICall()
    a.command = APICall_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()