'''
Created on 10.05.2013

@author: dbub
'''

import common
import PrivacyProxyAPI_pb2

if __name__ == '__main__':
    l = PrivacyProxyAPI_pb2.LoginData()
    l.username = "admin"
    l.password = "bla"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.login
    a.arguments = l.SerializeToString()
    
    test = common.Test("Successful login", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.LoginData,responseClass=PrivacyProxyAPI_pb2.LoginResponse)
    sessionID = test.run().sessionID
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.GetSettingsResponse)
    old_settings = test.run()
    
    s = PrivacyProxyAPI_pb2.UpdateSettingRequest()
    s.action = PrivacyProxyAPI_pb2.create
    s.data.type = PrivacyProxyAPI_pb2.creditcard
    s.data.description = "Test 123"
    s.data.hash = "fuuu"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Create setting", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.UpdateSettingRequest,responseClass=PrivacyProxyAPI_pb2.GetSettingsResponse)
    new_setting_id = test.run().entry[0].id
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.GetSettingsResponse)
    test.run()    
    
    s = PrivacyProxyAPI_pb2.UpdateSettingRequest()
    s.action = PrivacyProxyAPI_pb2.update
    s.data.id = new_setting_id
    s.data.type = PrivacyProxyAPI_pb2.creditcard
    s.data.description = "Test 321"
    s.data.hash = "lolol"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Update setting", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.UpdateSettingRequest)
    test.run()
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.GetSettingsResponse)
    test.run()
    
    s = PrivacyProxyAPI_pb2.UpdateSettingRequest()
    s.action = PrivacyProxyAPI_pb2.delete
    s.data.id = new_setting_id
    s.data.type = PrivacyProxyAPI_pb2.creditcard
    s.data.description = "Test 321"
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.updateSetting
    a.sessionKey = sessionID
    a.arguments = s.SerializeToString()
    
    test = common.Test("Remove setting", a, expectedSuccess=True,requestClass=PrivacyProxyAPI_pb2.UpdateSettingRequest)
    test.run()
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.getSettings
    a.sessionKey = sessionID
    
    test = common.Test("Get settings", a, expectedSuccess=True, responseClass=PrivacyProxyAPI_pb2.GetSettingsResponse)
    test.run()    
    
    a = PrivacyProxyAPI_pb2.APICall()
    a.command = PrivacyProxyAPI_pb2.logout
    a.sessionKey = sessionID
    
    test = common.Test("Successful logout", a, expectedSuccess=True)
    test.run()